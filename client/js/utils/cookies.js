export function getCookie(name) {
    const prefix = `${encodeURIComponent(name)}=`;
    const cookie = document.cookie
        .split(';')
        .map((part) => part.trim())
        .find((part) => part.startsWith(prefix));

    return cookie ? decodeURIComponent(cookie.slice(prefix.length)) : null;
}

export function setCookie(
    name,
    value,
    {
        path = '/',
        sameSite = 'Lax',
        secure = window.location.protocol === 'https:',
        expires,
        maxAge
    } = {}
) {
    const attributes = [
        `${encodeURIComponent(name)}=${encodeURIComponent(value)}`,
        `path=${path}`,
        `SameSite=${sameSite}`
    ];

    if (expires) {
        const expiresValue = expires instanceof Date
            ? expires.toUTCString()
            : expires;
        attributes.push(`expires=${expiresValue}`);
    }

    if (Number.isFinite(maxAge)) {
        attributes.push(`Max-Age=${maxAge}`);
    }

    if (secure) {
        attributes.push('Secure');
    }

    document.cookie = attributes.join('; ');
}

export function deleteCookie(name, options = {}) {
    setCookie(name, '', {
        ...options,
        expires: new Date(0),
        maxAge: 0
    });
}
