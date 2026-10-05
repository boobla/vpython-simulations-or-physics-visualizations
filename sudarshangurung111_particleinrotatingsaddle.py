from vpython import *
#GlowScript 3.2 VPython

# ==========================================
# 1. SCENE SETUP & CONSTANTS
# ==========================================
scene.title = "<b>Particle on a Solid Rotating Saddle Surface</b>"
scene.width = 900
scene.height = 550
scene.center = vec(0, 0, 0)
scene.forward = vec(-1, -1, -1)

# Physics Parameters
g = 9.81            # Acceleration due to gravity (m/s^2)
m = 0.1             # Particle mass (kg)
R = 1.0             # Saddle curvature parameter (m)
Omega = 3.5         # Surface rotation rate (rad/s)
dt = 0.0005         # Time step (s)

# Initial State
x = 0.2
y = 0.1
vx = 0.0
vy = 0.0
t = 0.0
running = False

# Function to compute saddle surface height z(x,y,t)
def get_z(x, y, t_curr):
    x_rot = x * cos(Omega * t_curr) + y * sin(Omega * t_curr)
    y_rot = -x * sin(Omega * t_curr) + y * cos(Omega * t_curr)
    return (x_rot**2 - y_rot**2) / (2.0 * R)

# ==========================================
# 2. SOLID SADDLE MESH GENERATION
# ==========================================
N_grid = 30
grid_size = 0.8
quad_faces = []

# Generate a continuous smooth quad mesh for the surface
for i in range(N_grid):
    for j in range(N_grid):
        q = quad(
            v0=vertex(pos=vec(0, 0, 0), color=color.cyan, opacity=0.8),
            v1=vertex(pos=vec(0, 0, 0), color=color.cyan, opacity=0.8),
            v2=vertex(pos=vec(0, 0, 0), color=color.cyan, opacity=0.8),
            v3=vertex(pos=vec(0, 0, 0), color=color.cyan, opacity=0.8)
        )
        quad_faces.append((i, j, q))

def update_saddle_mesh(t_curr):
    """Updates the vertices of the solid mesh to visually rotate the saddle."""
    dx = 2.0 * grid_size / N_grid
    dy = 2.0 * grid_size / N_grid
    
    for i, j, q in quad_faces:
        x0 = -grid_size + i * dx
        y0 = -grid_size + j * dy
        x1 = x0 + dx
        y1 = y0 + dy
        
        # Calculate vertices at (x, z, y)
        p0 = vec(x0, get_z(x0, y0, t_curr), y0)
        p1 = vec(x1, get_z(x1, y0, t_curr), y0)
        p2 = vec(x1, get_z(x1, y1, t_curr), y1)
        p3 = vec(x0, get_z(x0, y1, t_curr), y1)
        
        q.v0.pos = p0
        q.v1.pos = p1
        q.v2.pos = p2
        q.v3.pos = p3

# Initialize mesh geometry at t = 0
update_saddle_mesh(0)

# Central Rotating Axis
axis_line = cylinder(pos=vec(0, -0.8, 0), axis=vec(0, 1.6, 0), radius=0.01, color=color.gray(0.5))

# Particle Object
z_init = get_z(x, y, 0)
particle = sphere(pos=vec(x, z_init, y), radius=0.03, color=color.red, make_trail=True, trail_type="curve", interval=2, retain=300)
particle.trail_color = color.yellow

# Velocity Vector
scale_v = 0.2
arrow_vel = arrow(color=color.green, shaftwidth=0.008)

# Readout Display
info_label = label(pos=vec(0, 0.9, 0), text="", box=False, height=12, align="center")

# ==========================================
# 3. REAL-TIME GRAPHS
# ==========================================
graph_pos = graph(title="<b>Particle Position (x, y vs Time)</b>", xtitle="Time (s)", ytitle="Position (m)", width=440, height=200)
curve_x = gcurve(graph=graph_pos, color=color.blue, label="x (m)")
curve_y = gcurve(graph=graph_pos, color=color.red, label="y (m)")

graph_energy = graph(title="<b>Energy Exchange</b>", xtitle="Time (s)", ytitle="Energy (J)", width=440, height=200)
curve_ke = gcurve(graph=graph_energy, color=color.green, label="Kinetic")
curve_pe = gcurve(graph=graph_energy, color=color.orange, label="Potential")
curve_tot = gcurve(graph=graph_energy, color=color.black, label="Total Energy")

# ==========================================
# 4. CONTROLS & INTERACTIVE SLIDERS
# ==========================================
scene.append_to_caption("\n<b>Simulation Controls:</b>\n")

def toggle_run(b):
    global running
    running = not running
    b.text = "Pause" if running else "Play"

button(text="Play", bind=toggle_run)

def reset_sim():
    global x, y, vx, vy, t
    x = sl_x0.value
    y = sl_y0.value
    vx = 0.0
    vy = 0.0
    t = 0.0
    particle.clear_trail()
    curve_x.delete()
    curve_y.delete()
    curve_ke.delete()
    curve_pe.delete()
    curve_tot.delete()
    update_saddle_mesh(0)

button(text="Reset", bind=reset_sim)

scene.append_to_caption("\n\n<b>Adjust Parameters:</b>\n")

# Rotation Rate Slider
scene.append_to_caption("Rotation Rate Omega (rad/s): ")
def set_omega(s):
    global Omega
    Omega = s.value
    lbl_om.text = str(round(Omega, 2))
sl_om = slider(min=0.0, max=10.0, value=Omega, bind=set_omega)
lbl_om = wtext(text=str(Omega))

# Initial Positions
scene.append_to_caption(" | Initial X (m): ")
def set_x0(s):
    lbl_x0.text = str(round(s.value, 2))
sl_x0 = slider(min=-0.5, max=0.5, value=0.2, bind=set_x0)
lbl_x0 = wtext(text=str(sl_x0.value))

scene.append_to_caption(" | Initial Y (m): ")
def set_y0(s):
    lbl_y0.text = str(round(s.value, 2))
sl_y0 = slider(min=-0.5, max=0.5, value=0.1, bind=set_y0)
lbl_y0 = wtext(text=str(sl_y0.value))

# ==========================================
# 5. INTEGRATION LOOP
# ==========================================
while True:
    rate(1/dt)
    
    if running:
        # Re-render solid surface quad vertices for rotation
        update_saddle_mesh(t)
        
        # Derivatives of z(x,y,t)
        cos_w = cos(Omega * t)
        sin_w = sin(Omega * t)
        
        zx = (x * (cos_w**2 - sin_w**2) + 2.0 * y * cos_w * sin_w) / R
        zy = (y * (sin_w**2 - cos_w**2) + 2.0 * x * cos_w * sin_w) / R
        
        # Equations of Motion
        ax = -g * zx
        ay = -g * zy
        
        # Integration (Euler-Cromer)
        vx += ax * dt
        vy += ay * dt
        x += vx * dt
        y += vy * dt
        
        z = get_z(x, y, t)
        pz_dot = (vx * zx) + (vy * zy) + (Omega / R) * ((y**2 - x**2) * sin_w * cos_w + x * y * (cos_w**2 - sin_w**2))
        
        # Particle visual updates
        particle.pos = vec(x, z, y)
        arrow_vel.pos = particle.pos
        arrow_vel.axis = vec(vx, pz_dot, vy) * scale_v
        
        # Energies
        v_sq = vx**2 + vy**2 + pz_dot**2
        E_ke = 0.5 * m * v_sq
        E_pe = m * g * z
        E_tot = E_ke + E_pe
        
        # Graph updates
        curve_x.plot(t, x)
        curve_y.plot(t, y)
        curve_ke.plot(t, E_ke)
        curve_pe.plot(t, E_pe)
        curve_tot.plot(t, E_tot)
        
        # Label readout
        if int(t / dt) % 20 == 0:
            info_label.text = "<b>Time:</b> " + round(t, 2) + " s | " + \
                              "<b>Pos (x, y, z):</b> (" + round(x, 2) + ", " + round(y, 2) + ", " + round(z, 2) + ") m\n" + \
                              "<b>Total Energy:</b> " + round(E_tot, 4) + " J"
        
        t += dt