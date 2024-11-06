// PrivateRoute.js
import React, { useContext } from 'react';
import { Route, Redirect } from 'react-router-dom';
import { AuthContext } from './AuthContext';

const PrivateRoute = ({ component: Component, ...rest }) => {
    const { isAuthenticated, loading } = useContext(AuthContext);

    return (
        <Route
            {...rest}
            render={props =>
                loading ? (
                    <h3>Carregando...</h3>
                ) : isAuthenticated ? (
                    <Component {...props} />
                ) : (
                    <Redirect to="/login" />
                )
            }
        />
    );
};

export default PrivateRoute;
