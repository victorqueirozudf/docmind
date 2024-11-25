from rest_framework.views import APIView
from .serializers import AuthenticationSerializers
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64decode
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from django.contrib.sessions.models import Session
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.permissions import IsAdminUser
import os

class UserView(APIView):
    # Serializer serve para melhorar a comunicação entre as apis
    serializer_class = AuthenticationSerializers

    # Método para inserir dados
    def post(self, request):

        # Serializando e validando os dados recebidos
        serializer = AuthenticationSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Pegando o nome do usuário
        username = serializer.validated_data.get('username')

        # Pegado a senha encriptada
        encrypted_password = serializer.validated_data.get('password')

        key = os.getenv('KEY_CRYPTOGRAPHY').encode('utf-8')
        iv = os.getenv('IV_CRYPTOGRAPHY').encode('utf-8')

        # Definindo a cifra
        cipher = AES.new(key, AES.MODE_CBC, iv)

        # Descriptografando a senha
        decrypted_password = unpad(cipher.decrypt(b64decode(encrypted_password)), AES.block_size).decode('utf-8')

        # Verificando o usuário no banco de dados
        user = User.objects.filter(username=username).first()

        # Condicional que verifica se o usuário existe e se a senha está correta
        if user is None:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        elif not user.check_password(decrypted_password):
            return Response({'message': 'Incorrect password'}, status=status.HTTP_401_UNAUTHORIZED)

        # Definindo a sessão do usuário
        request.session['user_id'] = user.id
        request.session.set_expiry(999999)
        request.session.save()

        # Perguntar o que é
        refresh = RefreshToken.for_user(user)

        # Perguntar como funciona também
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'sessionid': request.session.session_key
        }, status=status.HTTP_200_OK)

    # Método que verifica se o usuário está logado e se é válido
    @staticmethod
    def verify_session(sessionid):
        try:
            session = Session.objects.get(session_key=sessionid)
            if session.expire_date > timezone.now():
                return True
            return False
        except Session.DoesNotExist:
            return

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        data = {
            'id': user.id,
            'username': user.username,
            'is_superuser': user.is_superuser
        }

        return Response(data, status=status.HTTP_200_OK)

class ListUsersView(APIView):
    # Apenas superusuários têm permissão para acessar este endpoint
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        # Verifica se o usuário é superusuário
        if not request.user.is_superuser:
            return Response({'message': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

        # Lista todos os usuários
        users = User.objects.all().values('id', 'username', 'is_superuser')
        return Response(users, status=status.HTTP_200_OK)

class RegisterUserView(APIView):
    def post(self, request):
        serializer = AuthenticationSerializers(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data.get('password', 'docmind123')

            encrypted_password = make_password(password)

            user = User.objects.create(
                username=username,
                password=encrypted_password
            )

            return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreateUserView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]  # Apenas superusuários podem criar novos usuários

    def post(self, request):
        try:
            username = request.data.get('username')
            password = request.data.get('password', 'docmind123')  # Define a senha padrão se não for fornecida
            is_superuser = request.data.get('is_superuser', False)  # Define se o usuário é superusuário

            # Verifica se o nome do usuário já existe
            if User.objects.filter(username=username).exists():
                return Response({'message': 'Usuário já existe.'}, status=status.HTTP_400_BAD_REQUEST)

            # Cria o usuário
            user = User.objects.create(
                username=username,
                password=make_password(password),
                is_superuser=is_superuser
            )

            return Response({'message': 'Usuário criado com sucesso.', 'username': user.username}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'message': f'Erro ao criar usuário: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, user_id):
        # Verifica se o usuário que faz a solicitação é um superusuário
        if not request.user.is_superuser:
            return Response({'message': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

        try:
            # Tenta encontrar o usuário pelo ID
            user = User.objects.get(id=user_id)

            if user == request.user:
                return Response({'message': 'Você não pode resetar sua senha para o padrão.'}, status=status.HTTP_400_BAD_REQUEST)

            # Define a senha padrão
            user.set_password(request.newPassword, 'docmind123')
            user.save()

            return Response({'message': 'Senha redefinida para "docmind123".'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'message': 'Usuário não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

class ChangePasswordView(APIView):
    """
    Endpoint para alterar a senha do usuário autenticado.
    """
    permission_classes = [IsAuthenticated]

    def put(self, request):
        # Obter dados do corpo da requisição
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        # Validações
        if not current_password or not new_password:
            return Response({"error": "Todos os campos são obrigatórios."}, status=status.HTTP_400_BAD_REQUEST)

        # Verifica se a senha atual está correta
        user = request.user
        if not check_password(current_password, user.password):
            return Response({"error": "Senha atual incorreta."}, status=status.HTTP_400_BAD_REQUEST)

        # Atualiza a senha do usuário
        user.password = make_password(new_password)
        user.save()

        return Response({"message": "Senha alterada com sucesso!"}, status=status.HTTP_200_OK)

class DeleteUserView(APIView):
    # Apenas superusuários podem acessar este endpoint
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, user_id):
        # Verifica se o usuário que faz a solicitação é um superusuário
        if not request.user.is_superuser:
            return Response({'message': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

        try:
            # Tenta encontrar o usuário pelo ID
            user = User.objects.get(id=user_id)

            # Não permite que o superusuário exclua a si mesmo
            if user == request.user:
                return Response({'message': 'Você não pode excluir a si mesmo.'}, status=status.HTTP_400_BAD_REQUEST)

            user.delete()  # Exclui o usuário
            return Response({'message': 'Usuário excluído com sucesso!'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'message': 'Usuário não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):

        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)

class VerifyTokenView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response(data={'message': 'Token is valid'}, status=status.HTTP_200_OK)