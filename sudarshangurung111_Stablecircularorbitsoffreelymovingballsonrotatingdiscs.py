from vpython import *
#GlowScript 3.2 VPython

# ==========================================
# 1. SCENE & CANVAS SETUP
# ==========================================
scene.title = "<b>Dynamic Rolling Ball on Rotating Disc (Weltner 1979)</b>"
scene.width = 900
scene.height = 550
scene.center = vec(0, 0, 0)
scene.forward = vec(0, -1, -2)

# Parameters
dt = 0.001          # Time step (s)
R_disc = 2.0        # Disc radius (m)
disc_thickness = 0.04
omega_d_mag = 2*pi  # Disc rotational speed (rad/s)

# Ball Parameters
m = 0.1             # Mass (kg)
R_ball = 0.12       # Ball radius (m)
g = 9.81            # Gravity (m/s^2)

# Solid sphere moment of inertia: alpha = 2/7
alpha = 2.0 / 7.0   

theta_tilt = 0.0   # Surface tilt angle
y_surface = disc_thickness / 2.0

# Vectors
omega_d = vec(0, omega_d_mag * cos(theta_tilt), -omega_d_mag * sin(theta_tilt))
F0 = vec(0, -m * g * sin(theta_tilt), 0)

# ==========================================
# 2. 3D VISUAL ELEMENTS WITH ROLL TEXTURE
# ==========================================
# Rotating Table / Disc
disc = cylinder(
    pos=vec(0, -disc_thickness/2.0, 0),
    axis=vec(0, disc_thickness, 0),
    radius=R_disc,
    color=color.gray(0.3),
    opacity=0.7
)

# Radial marker line on disc face
disc_line = cylinder(
    pos=vec(0, y_surface + 0.001, 0),
    axis=vec(R_disc, 0, 0),
    radius=0.008,
    color=color.yellow
)

# Rolling Ball with visual pattern (texture) to make 3D rotation visible
ball = sphere(
    pos=vec(0.5, y_surface + R_ball, 0),
    radius=R_ball,
    color=color.red,
    texture=textures.granite,  # Texture pattern highlights 3D spin
    make_trail=True,
    trail_color=color.cyan,
    trail_radius=0.004,
    retain=2000
)

# Attach equator stripes to the ball to make rotation even more dynamic
stripe1 = ring(pos=ball.pos, axis=vec(0,1,0), radius=R_ball*1.01, thickness=0.008, color=color.white)
stripe2 = ring(pos=ball.pos, axis=vec(1,0,0), radius=R_ball*1.01, thickness=0.008, color=color.yellow)

# Velocity Arrow
vel_arrow = cylinder(pos=ball.pos, axis=vec(0, 0, 0), radius=0.012, color=color.green)

# ==========================================
# 3. INTERACTIVE CONTROLS (PAUSE & SLIDERS)
# ==========================================
running = True

def toggle_pause(b):
    global running
    running = not running
    b.text = "<b>Pause</b>" if running else "<b>Play</b>"

button(text="<b>Pause</b>", bind=toggle_pause)

scene.append_to_caption("  |  <b>Disc Speed:</b> ")
def set_disc_speed(s):
    global omega_d_mag, omega_d
    omega_d_mag = s.value * pi
    omega_d = vec(0, omega_d_mag * cos(theta_tilt), -omega_d_mag * sin(theta_tilt))

slider(min=0.5, max=5.0, value=2.0, step=0.1, bind=set_disc_speed)

scene.append_to_caption("\n")

# ==========================================
# 4. INITIAL CONDITIONS & DYNAMIC LOOP
# ==========================================
v = vec(1.2, 0, 0.5) 
r = ball.pos

t = 0.0
disc_angle = 0.0

while True:
    rate(1/dt)
    
    if running:
        # Equation of Motion (Weltner 1979)
        accel = alpha * cross(omega_d, v) + (alpha / m) * F0
        accel.y = 0 
        
        # Translational Integration
        v += accel * dt
        r += v * dt
        
        # Position ball on table top
        r.y = y_surface + R_ball
        ball.pos = r
        
        # ----------------------------------------------------
        # DYNAMIC BALL SPIN / ROLL PHYSICS (No Slip Condition)
        # ----------------------------------------------------
        # Contact point disc velocity: v_disc = omega_d x r
        v_disc = cross(omega_d, r - vec(0, y_surface, 0))
        
        # Rotational velocity of ball surface relative to center: v_rel = v_disc - v
        v_rel = v_disc - v
        
        # Angular velocity vector of ball: omega_ball = (R x v_rel) / R^2
        R_vec = vec(0, -R_ball, 0)
        omega_ball = cross(R_vec, v_rel) / (R_ball**2)
        
        # Apply 3D rotation to the ball and its decorative stripes
        d_theta = mag(omega_ball) * dt
        if d_theta > 0:
            rot_axis = norm(omega_ball)
            ball.rotate(angle=d_theta, axis=rot_axis)
            stripe1.pos = ball.pos
            stripe1.rotate(angle=d_theta, axis=rot_axis, origin=ball.pos)
            stripe2.pos = ball.pos
            stripe2.rotate(angle=d_theta, axis=rot_axis, origin=ball.pos)
        
        # Visual updates
        vel_arrow.pos = ball.pos
        vel_arrow.axis = v * 0.25
        
        disc_angle += omega_d_mag * dt
        disc_line.axis = vec(R_disc * cos(disc_angle), 0, R_disc * sin(disc_angle))
        
        # Reset if ball leaves table
        if sqrt(r.x**2 + r.z**2) > R_disc:
            r = vec(0.5, y_surface + R_ball, 0)
            v = vec(1.2, 0, 0.5)
            ball.clear_trail()
            
        t += dt