#version 330 core

uniform sampler2D u_scene;
uniform float u_time;
uniform float u_night;
uniform float u_dusk;
uniform float u_enabled;
uniform vec2 u_texel_size;
uniform float u_temperature_grade;
uniform float u_saturation;
uniform float u_bloom_strength;

in vec2 uv;

out vec4 fragColor;

vec3 saturate_color(vec3 color, float amount) {
    float luminance = dot(color, vec3(0.2126, 0.7152, 0.0722));
    return mix(vec3(luminance), color, amount);
}

vec3 bright_part(vec3 color) {
    return max(color - vec3(0.68), vec3(0.0));
}

void main() {
    vec3 color = texture(u_scene, uv).rgb;
    if (u_enabled < 0.5) {
        fragColor = vec4(color, 1.0);
        return;
    }

    vec2 px = u_texel_size * 1.65;
    vec3 bloom = bright_part(texture(u_scene, uv + vec2(px.x, 0.0)).rgb);
    bloom += bright_part(texture(u_scene, uv - vec2(px.x, 0.0)).rgb);
    bloom += bright_part(texture(u_scene, uv + vec2(0.0, px.y)).rgb);
    bloom += bright_part(texture(u_scene, uv - vec2(0.0, px.y)).rgb);
    bloom += bright_part(texture(u_scene, uv + px).rgb);
    bloom += bright_part(texture(u_scene, uv - px).rgb);
    bloom *= 0.1667;

    vec3 graded = color;
    graded += bloom * u_bloom_strength;
    graded = mix(graded, graded * vec3(0.88, 0.94, 1.08), u_night * 0.20);
    graded = mix(graded, graded * vec3(1.07, 0.94, 0.86), u_dusk * 0.16);
    graded = mix(graded, graded * vec3(1.06, 1.00, 0.93), max(u_temperature_grade, 0.0));
    graded = mix(graded, graded * vec3(0.92, 0.98, 1.08), max(-u_temperature_grade, 0.0));
    graded = saturate_color(graded, u_saturation);

    vec2 center = uv - vec2(0.5);
    float vignette = smoothstep(0.82, 0.20, dot(center, center) * 2.15);
    graded *= 0.82 + vignette * 0.18;

    float scan = sin((uv.y + u_time * 0.015) * 620.0) * 0.0018;
    float grain = fract(sin(dot(uv * vec2(123.4, 456.7) + u_time, vec2(12.9898, 78.233))) * 43758.5453);
    graded += scan + (grain - 0.5) * 0.004;
    graded = graded / (graded + vec3(0.88));
    graded = pow(graded, vec3(0.92));

    fragColor = vec4(graded, 1.0);
}
