/**
 * Bilinear interpolation.
 */

float get(float *vals, int width, int x, int y) {
    return vals[y * width + x];
}

float bilinear(int width, float x, float y, float *vals) {
    float cap_width = (float)(width) - 0.0001;

    // Sanitize coordinates
    x = x < 0.0 ? 0.0 : x;
    x = x >= cap_width ? cap_width : x;

    y = y < 0.0 ? 0.0 : y;
    y = y >= cap_width ? cap_width : y;

    // Find corners of square
    int x_lo = x;
    int y_lo = y;
    int x_hi = x_lo + 1;
    int y_hi = y_lo + 1;

    // Get values of corners
    float val_a = get(vals, width, x_lo, y_lo);
    float val_b = get(vals, width, x_lo, y_hi);
    float val_c = get(vals, width, x_hi, y_lo);
    float val_d = get(vals, width, x_hi, y_hi);

    // Perform bilinear interpolation using weights
    float weight_a = (x_hi - x) * (y_hi - y);
    float weight_b = (x_hi - x) * (y - y_lo);
    float weight_c = (x - x_lo) * (y_hi - y);
    float weight_d = (y - y_lo) * (y - y_lo);

    return (
        weight_a * val_a +
        weight_b * val_b +
        weight_c * val_c +
        weight_d * val_d
    );
}
