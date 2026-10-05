from vpython import *
#GlowScript 3.2 VPython

# ==========================================
# 1. SCENE SETUP
# ==========================================
scene.title = "<b>Wilberforce Pendulum Dynamics with Force Vectors & Graphs</b>"
scene.width = 750
scene.height = 500
scene.center = vec(0, -0.6, 0)
scene.forward = vec(0, 0, -1)

# Default Physical Parameters
m = 0.50            # Mass (kg)
k = 5.0             # Linear spring constant (N/m)
delta = 0.005       # Torsional spring constant (N*m/rad)
epsilon = 0.024     # Coupling constant (N)
r_cyl = 0.045       # Cylinder radius (m)

dt = 0.001          # Time step (s)
g = 9.81            # Gravity (m/s^2)
L0 = 0.4            # Unstretched spring length (m)

# Dynamic variables
z = 0.08            # Initial translation displacement (m)
theta = 0.0         # Initial torsional displacement (rad)
vz = 0.0            # Vertical velocity
omega = 0.0         # Angular velocity
t = 0.0             # Time
running = False

# ==========================================
# 2. 3D VISUAL ELEMENTS & VECTOR ARROWS
# ==========================================
support = box(pos=vec(0, 0, 0), size=vec(0.2, 0.01, 0.2), color=color.gray(0.5))

z_eq = (m * g) / k
spring = helix(
    pos=vec(0, 0, 0),
    axis=vec(0, -(L0 + z_eq + z), 0),
    radius=0.035,
    coils=22,
    thickness=0.006,
    color=color.orange
)

h_cyl = 0.06
bob_pos = vec(0, -(L0 + z_eq + z), 0)
bob = cylinder(
    pos=bob_pos - vec(0, h_cyl/2.0, 0),
    axis=vec(0, h_cyl, 0),
    radius=r_cyl,
    color=color.cyan,
    opacity=0.8
)

marker = cylinder(
    pos=bob_pos + vec(0, h_cyl/2.0 + 0.001, 0),
    axis=vec(r_cyl * cos(theta), 0, r_cyl * sin(theta)),
    radius=0.003,
    color=color.yellow
)

# Vector Arrows for Forces and Torques
scale_force = 0.05
scale_torque = 5.0

arrow_restoring = arrow(color=color.red, shaftwidth=0.008)
arrow_coupling_f = arrow(color=color.magenta, shaftwidth=0.008)
arrow_torque_rest = arrow(color=color.green, shaftwidth=0.008)
arrow_torque_coup = arrow(color=color.orange, shaftwidth=0.008)

# ==========================================
# 3. REAL-TIME GRAPHS
# ==========================================
graph_motion = graph(title="<b>Displacement vs Time</b>", xtitle="Time (s)", ytitle="Value", width=500, height=220)
curve_z = gcurve(graph=graph_motion, color=color.blue, label="z (m)")
curve_theta = gcurve(graph=graph_motion, color=color.red, label="theta (rad)")

graph_energy = graph(title="<b>Energy Exchange</b>", xtitle="Time (s)", ytitle="Energy (J)", width=500, height=220)
curve_Etrans = gcurve(graph=graph_energy, color=color.blue, label="Translational")
curve_Erot = gcurve(graph=graph_energy, color=color.red, label="Rotational")
curve_Etotal = gcurve(graph=graph_energy, color=color.black, label="Total")

# ==========================================
# 4. INTERACTIVE INPUT PARAMETERS (UI)
# ==========================================
scene.append_to_caption("\n<b>Simulation Controls:</b>\n")

def toggle_run(b):
    global running
    running = not running
    b.text = "Pause" if running else "Play"

button(text="Play", bind=toggle_run)

def reset_sim():
    global z, theta, vz, omega, t
    z = sl_z0.value
    theta = radians(sl_th0.value)
    vz = 0.0
    omega = 0.0
    t = 0.0
    curve_z.delete()
    curve_theta.delete()
    curve_Etrans.delete()
    curve_Erot.delete()
    curve_Etotal.delete()

button(text="Reset", bind=reset_sim)

scene.append_to_caption("\n\n<b>Adjust Parameters:</b>\n")

# Slider: Mass
scene.append_to_caption("Mass m (kg): ")
def set_m(s):
    global m
    m = s.value
    lbl_m.text = str(round(m, 3))
sl_m = slider(min=0.1, max=1.0, value=m, bind=set_m)
lbl_m = wtext(text=str(m))

# Slider: Spring Constant k
scene.append_to_caption(" | k (N/m): ")
def set_k(s):
    global k
    k = s.value
    lbl_k.text = str(round(k, 2))
sl_k = slider(min=1.0, max=15.0, value=k, bind=set_k)
lbl_k = wtext(text=str(k))

# Slider: Coupling Constant epsilon
scene.append_to_caption("\nEpsilon (Coupling): ")
def set_eps(s):
    global epsilon
    epsilon = s.value
    lbl_eps.text = str(round(epsilon, 4))
sl_eps = slider(min=0.0, max=0.1, value=epsilon, bind=set_eps)
lbl_eps = wtext(text=str(epsilon))

# Slider: Initial z displacement
scene.append_to_caption(" | Initial z (m): ")
def set_z0(s):
    lbl_z0.text = str(round(s.value, 3))
sl_z0 = slider(min=-0.15, max=0.15, value=0.08, bind=set_z0)
lbl_z0 = wtext(text=str(sl_z0.value))

# Slider: Initial theta angle
scene.append_to_caption(" | Initial theta (deg): ")
def set_th0(s):
    lbl_th0.text = str(round(s.value, 1))
sl_th0 = slider(min=-180, max=180, value=0, bind=set_th0)
lbl_th0 = wtext(text=str(sl_th0.value))

# ==========================================
# 5. SIMULATION LOOP & VECTOR CALCULATIONS
# ==========================================
while True:
    rate(1/dt)
    
    # Calculate moment of inertia I = 0.5 * m * r^2
    I = 0.5 * m * (r_cyl**2)
    
    if running:
        # Coupled Equations of Motion:
        # m*d2z/dt2 + k*z + (epsilon/2)*theta = 0
        # I*d2theta/dt2 + delta*theta + (epsilon/2)*z = 0
        
        # Individual forces and torques
        F_restoring = -k * z
        F_coupling = -0.5 * epsilon * theta
        
        T_restoring = -delta * theta
        T_coupling = -0.5 * epsilon * z
        
        # Accelerations
        az = (F_restoring + F_coupling) / m
        alpha = (T_restoring + T_coupling) / I
        
        # Integration (Euler-Cromer)
        vz += az * dt
        omega += alpha * dt
        
        z += vz * dt
        theta += omega * dt
        
        # Update Visual Positions
        current_spring_len = L0 + (m * g / k) + z
        spring.axis = vec(0, -current_spring_len, 0)
        
        b_pos = vec(0, -current_spring_len, 0)
        bob.pos = b_pos - vec(0, h_cyl/2.0, 0)
        marker.pos = b_pos + vec(0, h_cyl/2.0 + 0.001, 0)
        marker.axis = vec(r_cyl * cos(theta), 0, r_cyl * sin(theta))
        
        # Update Force Vectors (positioned at bob center)
        arrow_restoring.pos = b_pos
        arrow_restoring.axis = vec(0, F_restoring * scale_force, 0)
        
        arrow_coupling_f.pos = b_pos + vec(0.01, 0, 0)
        arrow_coupling_f.axis = vec(0, F_coupling * scale_force, 0)
        
        # Update Torque Vectors (represented along axial direction)
        arrow_torque_rest.pos = b_pos
        arrow_torque_rest.axis = vec(0, T_restoring * scale_torque, 0)
        
        arrow_torque_coup.pos = b_pos + vec(-0.01, 0, 0)
        arrow_torque_coup.axis = vec(0, T_coupling * scale_torque, 0)
        
        # Calculate Energies
        E_trans = 0.5 * m * (vz**2) + 0.5 * k * (z**2)
        E_rot = 0.5 * I * (omega**2) + 0.5 * delta * (theta**2)
        E_coup = 0.5 * epsilon * z * theta
        E_total = E_trans + E_rot + E_coup
        
        # Update Real-time Graphs
        curve_z.plot(t, z)
        curve_theta.plot(t, theta)
        
        curve_Etrans.plot(t, E_trans)
        curve_Erot.plot(t, E_rot)
        curve_Etotal.plot(t, E_total)
        
        t += dt