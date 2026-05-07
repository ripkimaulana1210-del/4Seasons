#version 330 core

layout (location = 0) in vec3 in_normal;
layout (location = 1) in vec3 in_position;
layout (location = 2) in vec2 in_uv;

// Per-instance attributes
layout (location = 3) in vec4 in_model_col0;
layout (location = 4) in vec4 in_model_col1;
layout (location = 5) in vec4 in_model_col2;
layout (location = 6) in vec4 in_model_col3;
layout (location = 7) in vec3 in_instance_tint;
layout (location = 8) in vec2 in_instance_repeat;
layout (location = 9) in float in_instance_alpha;

uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_light_space;

out vec3 frag_pos;
out vec3 normal;
out vec2 uv;
out vec4 shadow_pos;
out vec3 v_tint;
out vec2 v_repeat;
out float v_alpha;

void main() {
    mat4 m_model = mat4(in_model_col0, in_model_col1, in_model_col2, in_model_col3);
    vec4 world_pos = m_model * vec4(in_position, 1.0);
    frag_pos = world_pos.xyz;
    normal = mat3(m_model) * in_normal;
    shadow_pos = m_light_space * world_pos;
    uv = in_uv;
    v_tint = in_instance_tint;
    v_repeat = in_instance_repeat;
    v_alpha = in_instance_alpha;
    gl_Position = m_proj * m_view * world_pos;
}
