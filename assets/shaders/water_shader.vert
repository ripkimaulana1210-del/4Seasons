#version 330

in vec3 in_normal;
in vec3 in_position;
in vec2 in_uv;

uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_model;
uniform mat4 m_light_space;
uniform float u_time;
uniform float u_wave_strength;

out vec3 v_world_pos;
out vec3 v_normal;
out float v_wave;
out vec2 v_uv;
out vec4 v_shadow_pos;

void main() {
    vec3 pos = in_position;

    float wave1 = sin(pos.x * 2.2 + u_time * 1.2) * 0.030;
    float wave2 = cos(pos.z * 2.8 - u_time * 1.0) * 0.022;
    float wave3 = sin((pos.x + pos.z) * 3.4 + u_time * 1.6) * 0.015;

    float wave = (wave1 + wave2 + wave3) * u_wave_strength;
    pos.y += wave;

    vec3 wave_normal = normalize(vec3(-wave1, 1.0, -wave2));
    vec3 local_normal = normalize(wave_normal * 0.85 + in_normal * 0.15);

    vec4 world_pos = m_model * vec4(pos, 1.0);

    mat3 normal_matrix = mat3(transpose(inverse(m_model)));
    v_normal = normalize(normal_matrix * local_normal);
    v_world_pos = world_pos.xyz;
    v_wave = wave;

    // Penting: in_uv harus dipakai agar tidak dibuang oleh compiler.
    v_uv = in_uv;
    v_shadow_pos = m_light_space * world_pos;

    gl_Position = m_proj * m_view * world_pos;
}
