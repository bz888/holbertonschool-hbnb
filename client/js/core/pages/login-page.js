import { loginUser } from '../api/auth-api.js';
import { getSafeLoginDestination } from '../auth/guard.js';
import { storeAuthToken } from '../auth/session.js';
import {
    clearMessage,
    setButtonState,
    showFormMessage
} from '../../utils/dom.js';

export function initLoginPage() {
    const form = document.getElementById('login-form');

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const emailInput = document.getElementById('email');
        const passwordInput = document.getElementById('password');
        const errorMessage = document.getElementById('login-error');
        const submitButton = form.querySelector('button[type="submit"]');
        clearMessage(errorMessage);

        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        setButtonState(submitButton, true, 'Logging in…');

        try {
            const token = await loginUser(
                emailInput.value.trim(),
                passwordInput.value
            );

            if (!storeAuthToken(token)) {
                throw new Error(
                    'Login succeeded, but the browser could not store your session. '
                    + 'Open HBNB through a local web server instead of directly from a file.'
                );
            }

            window.location.href = getSafeLoginDestination();
        } catch (error) {
            showFormMessage(errorMessage, error.message, true);
        } finally {
            setButtonState(submitButton, false, 'Login');
        }
    });
}
