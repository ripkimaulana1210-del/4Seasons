#version 330

struct Light {
    vec3 position;
    vec3 Ia;
    vec3 Id;
    vec3 Is;
};

uniform Light light;
uniform vec3 cam_pos;
uniform vec3 u_color;
uniform float u_time;
uniform float u_water_mode;
uniform float u_sparkle_strength;
uniform float u_season_mix;
uniform vec3 u_accent_color;
uniform vec3 u_fog_color;
uniform float u_fog_density;
uniform float u_fog_start;
uniform float u_fog_end;
uniform sampler2D u_shadow_map;
uniform float u_shadow_strength;

in vec3 v_world_pos;
in vec3 v_normal;
in float v_wave;
in vec2 v_uv;
in vec4 v_shadow_pos;

out vec4 fragColor;

float hash(vec2 p) {
    vec3 p3 = fract(vec3(p.xyx) * 0.1031);
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.x + p3.y) * p3.z);
}

vec3 apply_fog(vec3 color, vec3 world_pos) {
    float distance_to_camera = length(cam_pos - world_pos);
    float range_fog = smoothstep(u_fog_start, u_fog_end, distance_to_camera);
    float air_fog = 1.0 - exp(-distance_to_camera * u_fog_density * 0.030);
    float fog_amount = clamp(max(range_fog * u_fog_density, air_fog), 0.0, 0.74);
    return mix(color, u_fog_color, fog_amount);
}

float shadow_factor(vec3 N, vec3 L) {
    vec3 proj = v_shadow_pos.xyz / v_shadow_pos.w;
    proj = proj * 0.5 + 0.5;
    if (proj.z > 1.0 || proj.x < 0.0 || proj.x > 1.0 || proj.y < 0.0 || proj.y > 1.0) {
        return 1.0;
    }
    float bias = max(0.0030 * (1.0 - dot(N, L)), 0.0010);
    float closest = texture(u_shadow_map, proj.xy).r;
    float shadow = proj.z - bias > closest ? 1.0 : 0.0;
    return mix(1.0, 1.0 - u_shadow_strength * 0.34, shadow);
}

void main() {
    vec3 N = normalize(v_normal);
    vec3 L = normalize(light.position - v_world_pos);
    vec3 V = normalize(cam_pos - v_world_pos);
    vec3 H = normalize(L + V);

    float diff = max(dot(N, L), 0.0);

    float spec = pow(max(dot(N, H), 0.0), 96.0);
    spec *= 0.75;

    float fresnel = pow(1.0 - max(dot(N, V), 0.0), 2.8);

    vec3 deep_color = vec3(0.03, 0.15, 0.24);
    vec3 shallow_color = vec3(0.12, 0.34, 0.50);
    vec3 sky_reflect = vec3(0.52, 0.68, 0.86);

    float uv_ripple = sin((v_uv.x * 18.0 + v_uv.y * 21.0) + u_time * 0.9) * 0.035;
    float ripple_mask = 0.5 + v_wave * 8.0 + uv_ripple;
    ripple_mask = clamp(ripple_mask, 0.0, 1.0);

    vec3 base = mix(deep_color, shallow_color, ripple_mask);
    base = mix(base, u_color, 0.25);

    float spring = 1.0 - smoothstep(0.20, 0.75, abs(u_water_mode - 0.0));
    float summer = 1.0 - smoothstep(0.20, 0.75, abs(u_water_mode - 1.0));
    float autumn = 1.0 - smoothstep(0.20, 0.75, abs(u_water_mode - 2.0));
    float winter = 1.0 - smoothstep(0.20, 0.75, abs(u_water_mode - 3.0));

    float petal_glint = smoothstep(0.78, 0.98, hash(floor((v_uv + vec2(u_time * 0.018, 0.0)) * vec2(38.0, 31.0))));
    float summer_spark = pow(max(sin((v_world_pos.x + v_world_pos.z) * 6.0 + u_time * 2.6), 0.0), 18.0);
    float leaf_shadow = smoothstep(0.70, 0.96, hash(floor((v_uv + vec2(0.02 * sin(u_time), 0.0)) * vec2(20.0, 26.0))));
    float frost = max(
        1.0 - smoothstep(0.010, 0.045, abs(fract(v_uv.x * 10.0 + v_uv.y * 2.0) - 0.5)),
        1.0 - smoothstep(0.010, 0.035, abs(fract(v_uv.y * 12.0 - v_uv.x * 2.2) - 0.5))
    );

    base = mix(base, base + u_accent_color * petal_glint * 0.11, spring * u_season_mix);
    base = mix(base, base + vec3(1.0, 0.82, 0.34) * summer_spark * 0.24, summer * u_sparkle_strength);
    base = mix(base, base * vec3(0.86, 0.74, 0.58) + u_accent_color * leaf_shadow * 0.13, autumn * u_season_mix);
    base = mix(base, mix(base, vec3(0.54, 0.74, 0.86), 0.46) + frost * vec3(0.28, 0.46, 0.56) * 0.18, winter * u_season_mix);

    vec3 ambient = light.Ia * base * 1.2;
    vec3 diffuse = light.Id * diff * base * 0.9;
    vec3 reflection = sky_reflect * fresnel * 0.38;
    vec3 specular = light.Is * spec * vec3(1.0) * (0.65 + u_sparkle_strength * 0.70 + summer * 0.45);
    float shadow = shadow_factor(N, L);

    vec3 final_color = ambient + (diffuse + reflection + specular) * shadow;

    fragColor = vec4(apply_fog(final_color, v_world_pos), 0.96);
}
