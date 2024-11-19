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
from django.contrib.auth.hashers import make_password
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

        print(data)

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
            password = serializer.validated_data['password']

            encrypted_password = make_password(password)

            user = User.objects.create(
                username=username,
                password=encrypted_password
            )

            return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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