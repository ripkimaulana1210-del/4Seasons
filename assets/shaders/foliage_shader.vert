#version 330 core

layout (location = 0) in vec3 in_normal;
layout (location = 1) in vec3 in_position;

uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_model;
uniform mat4 m_light_space;
uniform float u_time;
uniform float u_wind_strength;

out vec3 frag_pos;
out vec3 normal;
out float sway_mix;
out float height_mix;
out vec4 shadow_pos;

void main() {
    vec3 pos = in_position;
    height_mix = smoothstep(0.10, 2.80, pos.y);

    float phase = u_time * (1.25 + u_wind_strength * 0.75) + pos.x * 4.7 + pos.z * 3.9;
    float secondary = sin(u_time * 0.82 + pos.x * 2.2 - pos.z * 2.8);
    sway_mix = sin(phase) * 0.5 + secondary * 0.5;

    vec3 wind_dir = normalize(vec3(0.82, 0.0, -0.48));
    pos += wind_dir * sway_mix * height_mix * (0.018 + u_wind_strength * 0.038);
    pos.y += cos(phase * 0.7) * height_mix * u_wind_strength * 0.010;

    vec4 world_pos = m_model * vec4(pos, 1.0);
    frag_pos = world_pos.xyz;
    normal = mat3(transpose(inverse(m_model))) * in_normal;
    shadow_pos = m_light_space * world_pos;

    gl_Position = m_proj * m_view * world_pos;
}
