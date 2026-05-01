#version 330 core

uniform vec3 u_top_color;
uniform vec3 u_mid_color;
uniform vec3 u_horizon_color;
uniform vec3 u_star_color;
uniform float u_star_intensity;
uniform float u_dusk;
uniform float u_night;
uniform float u_time;

in vec3 v_dir;

out vec4 fragColor;

float hash(vec2 p) {
    vec3 p3 = fract(vec3(p.xyx) * 0.1031);
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.x + p3.y) * p3.z);
}

float star_field(vec3 dir) {
    vec2 uv = vec2(atan(dir.z, dir.x) / 6.2831853 + 0.5, asin(dir.y) / 3.1415926 + 0.5);
    vec2 grid = floor(uv * vec2(220.0, 92.0));
    float cell = hash(grid);
    float star = smoothstep(0.992, 1.0, cell);
    float twinkle = 0.72 + 0.28 * sin(u_time * 2.4 + cell * 38.0);
    return star * twinkle * smoothstep(0.02, 0.45, dir.y);
}

void main() {
    float h = clamp(v_dir.y, 0.0, 1.0);
    vec3 color = mix(u_horizon_color, u_mid_color, smoothstep(0.00, 0.48, h));
    color = mix(color, u_top_color, smoothstep(0.35, 1.00, h));

    float dusk_band = exp(-pow((h - 0.14) * 6.0, 2.0)) * u_dusk;
    color += vec3(0.24, 0.10, 0.04) * dusk_band;

    float stars = star_field(normalize(v_dir)) * u_star_intensity;
    color = mix(color, u_star_color, stars);

    float vignette = smoothstep(-0.08, 0.28, v_dir.y);
    color *= mix(0.82, 1.0, vignette);
    color += vec3(0.012, 0.018, 0.040) * u_night * (1.0 - h);

    fragColor = vec4(color, 1.0);
}
