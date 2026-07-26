export function formatCoordinate(value) {
    const coordinate = Number(value);
    return Number.isFinite(coordinate) ? coordinate.toFixed(4) : 'Unknown';
}

export function formatPrice(value) {
    const price = Number(value);
    return Number.isFinite(price) ? `$${price.toFixed(2)}` : 'Price unavailable';
}

export function normalizeRating(value) {
    return Math.min(5, Math.max(0, Math.round(Number(value) || 0)));
}
