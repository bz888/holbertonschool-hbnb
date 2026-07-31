export function clearElement(element) {
    element.replaceChildren();
}

export function clearMessage(messageElement) {
    messageElement.hidden = true;
    messageElement.textContent = '';
}

export function showFormMessage(
    messageElement,
    message,
    isError = false
) {
    messageElement.textContent = message;
    messageElement.className = isError ? 'form-error' : 'form-success';
    messageElement.setAttribute('role', isError ? 'alert' : 'status');
    messageElement.hidden = false;
}

export function setButtonState(button, disabled, text) {
    button.disabled = disabled;
    button.textContent = text;
}
