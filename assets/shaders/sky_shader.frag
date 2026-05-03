#version 330 core

uniform vec3 u_top_color;
uniform vec3 u_mid_color;
uniform vec3 u_horizon_color;
uniform vec3 u_star_color;
uniform float u_star_intensity;
uniform float u_summer_sky_clarity;
uniform float u_season_index;
uniform float u_sky_detail_strength;
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

vec2 sky_delta(vec2 uv, vec2 center) {
    vec2 d = uv - center;
    d.x -= round(d.x);
    d.x *= 2.05;
    return d;
}

float soft_disc(vec2 uv, vec2 center, float radius) {
    radius *= 0.42;
    float d = length(sky_delta(uv, center));
    return 1.0 - smoothstep(radius, radius * 1.85, d);
}

float sky_line(vec2 uv, vec2 a, vec2 b, float width) {
    width *= 0.36;
    vec2 p = vec2(uv.x * 2.05, uv.y);
    vec2 pa = p - vec2(a.x * 2.05, a.y);
    vec2 ba = vec2((b.x - a.x) * 2.05, b.y - a.y);
    float h = clamp(dot(pa, ba) / max(dot(ba, ba), 0.0001), 0.0, 1.0);
    float d = length(pa - ba * h);
    return 1.0 - smoothstep(width, width * 2.7, d);
}

float constellation_node(vec2 uv, vec2 center, float radius) {
    radius *= 0.40;
    float d = length(sky_delta(uv, center));
    float core = 1.0 - smoothstep(radius, radius * 1.8, d);
    float halo = 1.0 - smoothstep(radius * 1.8, radius * 5.0, d);
    return core + halo * 0.14;
}

float constellation_field(vec2 uv) {
    float lines = 0.0;
    float nodes = 0.0;

    vec2 a0 = vec2(0.16, 0.69);
    vec2 a1 = vec2(0.20, 0.73);
    vec2 a2 = vec2(0.25, 0.71);
    vec2 a3 = vec2(0.29, 0.76);
    vec2 a4 = vec2(0.34, 0.79);
    lines += sky_line(uv, a0, a1, 0.0032);
    lines += sky_line(uv, a1, a2, 0.0032);
    lines += sky_line(uv, a2, a3, 0.0032);
    lines += sky_line(uv, a3, a4, 0.0032);
    nodes += constellation_node(uv, a0, 0.0060) + constellation_node(uv, a1, 0.0055);
    nodes += constellation_node(uv, a2, 0.0052) + constellation_node(uv, a3, 0.0064);
    nodes += constellation_node(uv, a4, 0.0070);

    vec2 b0 = vec2(0.53, 0.58);
    vec2 b1 = vec2(0.57, 0.63);
    vec2 b2 = vec2(0.61, 0.58);
    vec2 b3 = vec2(0.58, 0.53);
    vec2 b4 = vec2(0.64, 0.66);
    vec2 b5 = vec2(0.68, 0.70);
    lines += sky_line(uv, b0, b1, 0.0030);
    lines += sky_line(uv, b1, b2, 0.0030);
    lines += sky_line(uv, b2, b3, 0.0030);
    lines += sky_line(uv, b3, b0, 0.0030);
    lines += sky_line(uv, b1, b4, 0.0028);
    lines += sky_line(uv, b4, b5, 0.0028);
    nodes += constellation_node(uv, b0, 0.0050) + constellation_node(uv, b1, 0.0062);
    nodes += constellation_node(uv, b2, 0.0050) + constellation_node(uv, b3, 0.0048);
    nodes += constellation_node(uv, b4, 0.0055) + constellation_node(uv, b5, 0.0064);

    vec2 c0 = vec2(0.76, 0.62);
    vec2 c1 = vec2(0.80, 0.67);
    vec2 c2 = vec2(0.84, 0.64);
    vec2 c3 = vec2(0.88, 0.70);
    vec2 c4 = vec2(0.92, 0.74);
    lines += sky_line(uv, c0, c1, 0.0029);
    lines += sky_line(uv, c1, c2, 0.0029);
    lines += sky_line(uv, c2, c3, 0.0029);
    lines += sky_line(uv, c3, c4, 0.0029);
    nodes += constellation_node(uv, c0, 0.0054) + constellation_node(uv, c1, 0.0050);
    nodes += constellation_node(uv, c2, 0.0057) + constellation_node(uv, c3, 0.0052);
    nodes += constellation_node(uv, c4, 0.0066);

    return lines * 0.42 + nodes * 0.82;
}

vec3 summer_planets(vec2 uv) {
    vec3 color = vec3(0.0);

    float venus = soft_disc(uv, vec2(0.36, 0.58), 0.010);
    float venus_halo = soft_disc(uv, vec2(0.36, 0.58), 0.026);
    color += vec3(1.00, 0.92, 0.70) * venus * 1.35 + vec3(1.00, 0.74, 0.38) * venus_halo * 0.18;

    float jupiter = soft_disc(uv, vec2(0.72, 0.66), 0.014);
    float jupiter_halo = soft_disc(uv, vec2(0.72, 0.66), 0.034);
    color += vec3(0.96, 0.82, 0.58) * jupiter * 1.12 + vec3(0.80, 0.68, 0.46) * jupiter_halo * 0.16;

    float mars = soft_disc(uv, vec2(0.55, 0.50), 0.008);
    color += vec3(1.00, 0.40, 0.24) * mars * 1.10;

    vec2 saturn_center = vec2(0.20, 0.63);
    vec2 saturn_d = sky_delta(uv, saturn_center);
    float saturn = soft_disc(uv, saturn_center, 0.010);
    float ring_dist = abs(length(saturn_d * vec2(0.88, 2.85)) - 0.014);
    float ring = (1.0 - smoothstep(0.0010, 0.0032, ring_dist)) * (1.0 - smoothstep(0.010, 0.026, length(saturn_d)));
    color += vec3(0.94, 0.78, 0.50) * saturn * 0.72 + vec3(0.92, 0.72, 0.45) * ring * 0.22;

    return color;
}

vec3 summer_galaxy(vec3 dir, vec2 uv) {
    float path = 0.56 + 0.12 * sin((uv.x + 0.08) * 6.2831853) + 0.035 * sin((uv.x + 0.32) * 18.0);
    float dist = abs(uv.y - path);
    float wide = exp(-pow(dist * 14.0, 2.0));
    float core = exp(-pow(dist * 31.0, 2.0));
    float grain_a = hash(floor(uv * vec2(520.0, 190.0)));
    float grain_b = hash(floor(uv * vec2(105.0, 44.0)) + 9.7);
    float sky_mask = smoothstep(0.10, 0.45, dir.y);
    float dust = smoothstep(0.34, 0.88, grain_b);

    vec3 blue_haze = vec3(0.12, 0.18, 0.48) * wide * (0.18 + grain_a * 0.26);
    vec3 pale_core = vec3(0.68, 0.58, 0.94) * core * (0.12 + grain_a * 0.30);
    return (blue_haze + pale_core) * (1.0 - dust * 0.36) * sky_mask;
}

float season_mask(float target) {
    return 1.0 - smoothstep(0.20, 0.76, abs(u_season_index - target));
}

vec3 spring_rainbow(vec2 uv, float h) {
    vec2 center = vec2(0.55, -0.04);
    vec2 d = vec2((uv.x - center.x) * 1.78, uv.y - center.y);
    float radius = length(d);
    float arc = 1.0 - smoothstep(0.010, 0.034, abs(radius - 0.56));
    arc *= smoothstep(0.08, 0.32, h) * (1.0 - smoothstep(0.46, 0.72, h));

    float band = clamp((radius - 0.535) / 0.050, 0.0, 1.0);
    vec3 red = vec3(1.00, 0.34, 0.28);
    vec3 yellow = vec3(1.00, 0.88, 0.34);
    vec3 green = vec3(0.34, 0.86, 0.52);
    vec3 blue = vec3(0.36, 0.66, 1.00);
    vec3 color = mix(red, yellow, smoothstep(0.00, 0.33, band));
    color = mix(color, green, smoothstep(0.25, 0.64, band));
    color = mix(color, blue, smoothstep(0.58, 1.00, band));
    return color * arc * (0.30 + u_dusk * 0.20) * (1.0 - u_night);
}

vec3 autumn_cloud_detail(vec2 uv, float h) {
    float band = exp(-pow((h - 0.46) * 4.2, 2.0));
    float n1 = hash(floor((uv + vec2(u_time * 0.004, 0.0)) * vec2(26.0, 9.0)));
    float n2 = hash(floor((uv + vec2(0.13, u_time * 0.003)) * vec2(48.0, 15.0)));
    float mottled = smoothstep(0.34, 0.82, mix(n1, n2, 0.42));
    vec3 cloud = mix(vec3(0.14, 0.10, 0.08), vec3(0.45, 0.30, 0.18), mottled);
    return cloud * band * (0.16 + u_dusk * 0.20) * (1.0 - u_night * 0.38);
}

vec3 winter_aurora_detail(vec2 uv, float h) {
    float ribbon_a = exp(-pow((h - (0.62 + 0.055 * sin(uv.x * 10.0 + u_time * 0.35))) * 18.0, 2.0));
    float ribbon_b = exp(-pow((h - (0.76 + 0.040 * sin(uv.x * 14.0 - u_time * 0.42))) * 24.0, 2.0));
    float curtain = smoothstep(0.10, 0.55, h) * smoothstep(0.98, 0.58, h);
    float shimmer = 0.72 + 0.28 * sin(u_time * 1.7 + uv.x * 31.0);
    vec3 green = vec3(0.28, 1.00, 0.72);
    vec3 blue = vec3(0.30, 0.60, 1.00);
    return (green * ribbon_a + blue * ribbon_b * 0.74) * curtain * shimmer * u_night * 0.26;
}

float star_layer(vec2 uv, vec2 density, float threshold, float base_size, float brightness, float twinkle_speed) {
    vec2 grid = uv * density;
    vec2 id = floor(grid);
    vec2 cell = fract(grid);

    float seed = hash(id);
    float visible = step(threshold, seed);
    vec2 star_pos = vec2(hash(id + 17.31), hash(id + 61.73));
    float size = base_size * mix(0.58, 1.42, hash(id + 8.17));
    float dist_to_star = length(cell - star_pos);
    float point = 1.0 - smoothstep(0.0, size, dist_to_star);
    point *= point;
    float twinkle = 0.64 + 0.36 * sin(u_time * twinkle_speed + seed * 42.0);

    return point * visible * brightness * twinkle;
}

float star_mist(vec3 dir, vec2 uv) {
    float tilted_band = abs(dir.y * 0.82 + dir.x * 0.15 - dir.z * 0.10);
    float band = exp(-pow(tilted_band * 5.8, 2.0));
    float grain_a = hash(floor(uv * vec2(170.0, 70.0)));
    float grain_b = hash(floor(uv * vec2(410.0, 150.0)) + 19.2);
    float grain = mix(grain_a, grain_b, 0.45);
    return band * (0.050 + grain * 0.105) * smoothstep(0.03, 0.60, dir.y);
}

float star_field(vec3 dir) {
    vec2 uv = vec2(atan(dir.z, dir.x) / 6.2831853 + 0.5, asin(dir.y) / 3.1415926 + 0.5);
    float sky_mask = smoothstep(-0.02, 0.22, dir.y);

    float stars = 0.0;
    stars += star_layer(uv, vec2(380.0, 155.0), 0.950, 0.030, 0.44, 1.8);
    stars += star_layer(uv, vec2(250.0, 105.0), 0.922, 0.036, 0.27, 1.2);
    stars += star_layer(uv, vec2(145.0, 64.0), 0.974, 0.052, 0.82, 2.7);
    stars += star_layer(uv, vec2(74.0, 34.0), 0.986, 0.075, 1.18, 3.5);
    stars += star_mist(dir, uv);

    return stars * sky_mask;
}

void main() {
    vec3 dir = normalize(v_dir);
    vec2 uv = vec2(atan(dir.z, dir.x) / 6.2831853 + 0.5, asin(dir.y) / 3.1415926 + 0.5);
    float h = clamp(v_dir.y, 0.0, 1.0);
    vec3 color = mix(u_horizon_color, u_mid_color, smoothstep(0.00, 0.48, h));
    color = mix(color, u_top_color, smoothstep(0.35, 1.00, h));

    float dusk_band = exp(-pow((h - 0.14) * 6.0, 2.0)) * u_dusk;
    color += vec3(0.24, 0.10, 0.04) * dusk_band;

    float stars = clamp(star_field(dir) * u_star_intensity, 0.0, 1.35);
    color += u_star_color * stars * (0.72 + u_night * 0.35);

    float spring = season_mask(0.0);
    float summer = season_mask(1.0);
    float autumn = season_mask(2.0);
    float winter = season_mask(3.0);
    float detail = u_sky_detail_strength;

    color += spring_rainbow(uv, h) * spring * detail;

    float summer_night = u_summer_sky_clarity * smoothstep(0.42, 0.92, u_night) * (1.0 - u_dusk * 0.54);
    color += summer_galaxy(dir, uv) * summer_night * 0.62 * detail * (0.55 + summer * 0.45);
    color += summer_planets(uv) * summer_night * smoothstep(0.05, 0.28, dir.y) * 0.48 * detail;

    float constellations = constellation_field(uv) * summer_night * smoothstep(0.12, 0.38, dir.y);
    color += vec3(0.62, 0.76, 1.00) * constellations * 0.30;
    color = mix(color, color + autumn_cloud_detail(uv, h) * detail, autumn * 0.75);
    color += winter_aurora_detail(uv, h) * winter * detail;

    float vignette = smoothstep(-0.08, 0.28, v_dir.y);
    color *= mix(0.82, 1.0, vignette);
    color += vec3(0.012, 0.018, 0.040) * u_night * (1.0 - h);

    fragColor = vec4(color, 1.0);
}
