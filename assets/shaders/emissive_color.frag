#version 330 core

uniform vec3 u_color;
uniform float u_alpha;

out vec4 fragColor;

void main() {
    fragColor = vec4(u_color, u_alpha);
}
