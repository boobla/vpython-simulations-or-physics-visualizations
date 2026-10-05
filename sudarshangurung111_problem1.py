from vpython import *
#Web VPython 3.2


# ==========================================
# 1. SCENE & CANVAS SETUP
# ==========================================
scene.title = "<b>Problem 2001: Elastic Pendulum (Spring-Mass System)</b>"
scene.width = 900
scene.height = 600
scene.center = vec(0, -1.2, 0)
scene.forward = vec(0, 0, -1)

# Simulation Parameters
dt = 0.001          # Time step (s)
g = 9.81            # Gravity (m/s^2)
m = 1.0             # Mass (kg)
k = 40.0            # Spring constant (N/m)
l0 = 1.0            # Unstretched spring rest length (m)

# Equilibrium hanging length r0
r0 = l0 + (m * g) / k

# Frequencies
omega_s = sqrt(k / m)        # Spring frequency
omega_p = sqrt(g / r0)       # Pendulum frequency

# Initial Conditions (Problem 2001 Part c)
# Initial perturbation: lambda_0 = A, d(theta)/dt = omega_p * B
A_init = 0.15                # Relative stretch perturbation lambda = (r - r0)/r0
B_init = 0.20                # Angular velocity factor

theta = 0.0                  # Initial angle theta_0
r = r0 * (1.0 + A_init)      # Initial radial distance r_0
dr = 0.0                     # Initial radial velocity
dtheta = omega_p * B_init    # Initial angular velocity

# ==========================================
# 2. VISUAL ELEMENTS & DECORATIONS
# ==========================================
# Fixed Pivot Point
pivot = sphere(pos=vec(0, 0, 0), radius=0.04, color=color.gray(0.5))

# Vertical Equilibrium Reference Line (Dashed appearance)
ref_line = cylinder(pos=vec(0, 0, 0), axis=vec(0, -r0*1.5, 0), radius=0.002, color=color.gray(0.3), opacity=0.5)

# Helical Spring
spring = helix(
    pos=pivot.pos,
    axis=vec(r * sin(theta), -r * cos(theta), 0),
    radius=0.05,
    coils=15,
    color=color.orange,
    thickness=0.012
)

# Attached Mass
bob = sphere(
    pos=pivot.pos + spring.axis,
    radius=0.08,
    color=color.red,
    make_trail=True,
    trail_color=color.cyan,
    trail_radius=0.003,
    retain=3000
)

# Energy & Physics Info Label
info_label = label(
    pos=vec(-1.2, 0.3, 0),
    text="",
    box=False,
    height=12,
    align="left"
)

# ==========================================
# 3. INTERACTIVE CONTROLS
# ==========================================
running = True

def toggle_pause(b):
    global running
    running = not running
    b.text = "<b>Pause</b>" if running else "<b>Play</b>"

button(text="<b>Pause</b>", bind=toggle_pause)

def reset_sim():
    global r, theta, dr, dtheta, t
    r = r0 * (1.0 + A_init)
    theta = 0.0
    dr = 0.0
    dtheta = omega_p * B_init
    t = 0.0
    bob.clear_trail()

button(text="<b>Reset</b>", bind=reset_sim)

# ==========================================
# 4. NUMERICAL INTEGRATION LOOP
# ==========================================
t = 0.0

while True:
    rate(1/dt)
    
    if running:
        # 1. Calculate Exact Non-Linear Second Derivatives (Lagrange Equations)
        # d2r/dt2 = r * (dtheta)^2 + g * cos(theta) - (k/m) * (r - l0)
        d2r = r * (dtheta**2) + g * cos(theta) - (k / m) * (r - l0)
        
        # d2theta/dt2 = -(2 * dr * dtheta + g * sin(theta)) / r
        d2theta = -(2.0 * dr * dtheta + g * sin(theta)) / r
        
        # 2. Integrate Velocities and Positions (Euler-Cromer)
        dr += d2r * dt
        dtheta += d2theta * dt
        
        r += dr * dt
        theta += dtheta * dt
        
        # 3. Update 3D Visual Positions
        bob_pos = vec(r * sin(theta), -r * cos(theta), 0)
        spring.axis = bob_pos
        bob.pos = bob_pos
        
        # 4. Energy Calculations for Verification
        T = 0.5 * m * (dr**2 + (r * dtheta)**2)
        V = -m * g * r * cos(theta) + 0.5 * k * ((r - l0)**2)
        E_total = T + V
        
        lambda_val = (r - r0) / r0
        
        # 5. Live Info Display
        if int(t / dt) % 20 == 0:
            info_label.text = "<b>Time:</b> " + round(t, 2) + " s\n" + \
                              "<b>r:</b> " + round(r, 3) + " m\n" + \
                              "<b>Theta:</b> " + round(degrees(theta), 2) + " deg\n" + \
                              "<b>Perturbation (lambda):</b> " + round(lambda_val, 3) + "\n" + \
                              "<b>Total Energy:</b> " + round(E_total, 3) + " J"
        
        t += dt