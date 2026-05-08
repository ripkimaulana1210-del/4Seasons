#version 330 core

layout (location = 0) in vec3 in_normal;
layout (location = 1) in vec3 in_position;

// Per-instance attributes
layout (location = 2) in vec4 in_model_col0;
layout (location = 3) in vec4 in_model_col1;
layout (location = 4) in vec4 in_model_col2;
layout (location = 5) in vec4 in_model_col3;
layout (location = 6) in vec3 in_instance_color;
layout (location = 7) in float in_instance_alpha;

uniform mat4 m_proj;
uniform mat4 m_view;

out vec3 v_color;
out float v_alpha;

void main() {
    mat4 m_model = mat4(in_model_col0, in_model_col1, in_model_col2, in_model_col3);
    v_color = in_instance_color;
    v_alpha = in_instance_alpha;
    vec3 position = in_position + in_normal * 0.000001;
    gl_Position = m_proj * m_view * m_model * vec4(position, 1.0);
}
