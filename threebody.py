from vpython import *
import random

celestials = []
N = 3
G = 9.81 # gravitational constant
WIDTH=1200
HEIGHT=600#850
SLIDER_LEN=WIDTH/8
SIMULATION_START=False
sliders = []

#config
RADIUS=50
MASS=200
SUN_TRAIL=True
VEL_COLOR=color.blue
FORCE_COLOR=color.red
INIT_POS_MIN=-1000
INIT_POS_MAX=1000
INIT_VEL_MIN=-1
INIT_VEL_MAX=1
GRAV_ARROWS_ON=True
LABELS_ON=True
VEL_ARROWS_ON=True

class Celestial:
    def __init__(self, mass, sphere, velarrow, isSun=True, poslabel=None, velocity=None, name=None):
        self.idx = str(sphere.idx)
        self.mass = mass
        self.sphere = sphere
        self.poslabel = poslabel
        self.isSun = isSun
        self.velarrow = velarrow
        self.name = name
        self.sliders = []
        self.g_vecs = {} # map of gravity arrows
        self.total_grav = vec(0,0,0)
        self.wt = None
        if velocity:
            self.velocity = velocity
        else:
            self.velocity = vec(0,0,0)
    
    @property
    def pos(self):
        return self.sphere.pos

    @pos.setter
    def pos(self, value):
        self.sphere.pos = value
        self.poslabel.pos = value
        self.velarrow.pos = value
        self.poslabel.text = str(value).strip("<>")
        for c in celestials:
            calc_gravity(c, celestials)
        self.wt.text=f"({str(value).strip('<>')}) {self.vel}"

    @property
    def vel(self):
        return self.velocity

    @vel.setter
    def vel(self, value):
        self.velocity = value
        self.velarrow.axis = value
        self.wt.text=f"({str(self.pos).strip('<>')}) {value}"

    def show_velarrow(self):
        self.velarrow.visible=True

    def hide_velarrow(self):
        self.velarrow.visible=False


def calc_gravity(obj, celestials):
    # assume objects have unique indexes in VPython
    total_grav = vec(0, 0, 0)
    for other in celestials:
        if other.idx != obj.idx:
            r = other.sphere.pos - obj.sphere.pos
         #   print(r)
            mag = G * obj.mass * other.mass / (r.mag * r.mag)
            dirc = other.pos - obj.pos
            grav = dirc/dirc.mag * mag
         #   print(f"{obj.name}<-{other.name} grav=", grav)
            if GRAV_ARROWS_ON: 
                if other.name not in obj.g_vecs:
                    obj.g_vecs[other.name] = arrow(pos=obj.pos, axis=grav, color=FORCE_COLOR, opacity=0.5)
                else:
                    obj.g_vecs[other.name].pos = obj.pos
                    obj.g_vecs[other.name].axis = grav
                    obj.g_vecs[other.name].visible = True
            else:
                for k in obj.g_vecs.keys():
                    obj.g_vecs[k].visible = False
            total_grav = total_grav + grav
    obj.total_grav = total_grav
    return total_grav


def do_input():
    k = keysdown()
    # WS-y, AD-x, uparrow downarrow-z, QE rotate about +-z, ZX rotate about +-x (horizontal)
    # = to go back to home (also make a button)
    # P for showing position
    # V for showing velocity
    # G for showing gravity vectors
    # follow button to follow an object

def do_slider(evt):
    idx, pos_or_vel, coord = evt.id.split("-") # coord is "x", "y", or "z"
    obj = [x for x in celestials if x.idx == idx][0]
    if pos_or_vel == "pos":
        setattr(obj.poslabel.pos, coord, evt.value)
        setattr(obj.sphere.pos, coord, evt.value)
        setattr(obj.velarrow.pos, coord, evt.value)
        obj.poslabel.text = str(obj.sphere.pos).strip("<>")
        obj.wt.text=f"({str(obj.pos).strip('<>')}) {obj.vel}"
    elif pos_or_vel == "vel":
        setattr(obj.velocity, coord, evt.value)
        setattr(obj.velarrow.axis, coord, evt.value)
        obj.wt.text=f"({str(obj.pos).strip('<>')}) {obj.vel}"
    obj.sphere.clear_trail()
    
def randomize(evt):
    _, i = evt.id.split("-")
    obj = celestials[int(i)]
    x = random.randrange(INIT_POS_MIN, INIT_POS_MAX)
    y = random.randrange(INIT_POS_MIN, INIT_POS_MAX)
    z = random.randrange(INIT_POS_MIN, INIT_POS_MAX)
    obj.pos = vec(x,y,z)    
    x = random.randrange(INIT_VEL_MIN*100, INIT_VEL_MAX*100)/100
    y = random.randrange(INIT_VEL_MIN*100, INIT_VEL_MAX*100)/100
    z = random.randrange(INIT_VEL_MIN*100, INIT_VEL_MAX*100)/100
    obj.vel = vec(x,y,z)    
    obj.sphere.clear_trail()

def toggle_simulation(evt):
    global SIMULATION_START
    if SIMULATION_START is False:
        SIMULATION_START = True
        print("Starting simulation")
        goButton.text = "Stop"
        goButton.background = color.red
        # disable all sliders
        for s in sliders:
            s.disabled = True
        for c in celestials:
            print(f"{c.name} grav", calc_gravity(c, celestials))
    else:
        SIMULATION_START = False
        goButton.text = "Start"
        goButton.background = color.green
        # enable all sliders
        for s in sliders:
            s.disabled = False

def toggle_grav(evt):
    global GRAV_ARROWS_ON
    if GRAV_ARROWS_ON is False:
        GRAV_ARROWS_ON = True
        gravToggleButton.text = "Gravity arrows are ON"
        gravToggleButton.background = color.yellow
        for c in celestials:
            calc_gravity(c, celestials)
    else:
        GRAV_ARROWS_ON = False
        gravToggleButton.text = "Gravity arrows are OFF"
        gravToggleButton.background = vec(0.5,0.5,0.5)

def toggle_labels(evt):
    global LABELS_ON
    if LABELS_ON is False:
        LABELS_ON = True
        lablToggleButton.text = "Labels are ON"
        lablToggleButton.background = color.yellow
        for c in celestials:
            c.poslabel.visible = True
    else:
        LABELS_ON = False
        lablToggleButton.text = "Labels are OFF"
        lablToggleButton.background = vec(0.5,0.5,0.5)
        for c in celestials:
            c.poslabel.visible = False


def toggle_vel(evt):
    global VEL_ARROWS_ON
    if VEL_ARROWS_ON is False:
        VEL_ARROWS_ON = True
        velToggleButton.text = "Velocity arrows are ON"
        velToggleButton.background = color.yellow
        for c in celestials:
            c.show_velarrow()
    else:
        VEL_ARROWS_ON = False
        velToggleButton.text = "Velocity arrows are OFF"
        velToggleButton.background = vec(0.5,0.5,0.5)
        for c in celestials:
            c.hide_velarrow()


scene = canvas(width=WIDTH, height=HEIGHT, title="Welcome to Three Body.")
random.seed(1980)
for i in range(N):
    pos = vec(random.randrange(INIT_POS_MIN,INIT_POS_MAX),random.randrange(INIT_POS_MIN,INIT_POS_MAX),random.randrange(INIT_POS_MIN,INIT_POS_MAX))
    sph = sphere(pos=pos, radius=RADIUS, color=vec(1, 1-0.2*i, 0), opacity=0.7,
                 make_trail=SUN_TRAIL, interval=10, retain=-1) 
    lbl = label(pos = sph.pos, text=str(sph.pos).strip("<>"), opacity=0, border=0, box=0)
    velarr = arrow(pos=sph.pos, axis=vec(0,0,0), color=VEL_COLOR)
    celestial = Celestial(MASS, sph, velarr, poslabel=lbl, name=f"sun{i+1}")
    scene.append_to_caption(f"sun{i+1} position: ")
    scene.append_to_caption("x")
    sliderx = slider(bind=do_slider, max=1000, min = -1000, step=1, value=sph.pos.x, 
                     id=f'{sph.idx}-pos-x', length=SLIDER_LEN)
    scene.append_to_caption("y")
    slidery = slider(bind=do_slider, max=1000, min = -1000, step=1, value=sph.pos.y, 
                     id=f'{sph.idx}-pos-y', length=SLIDER_LEN)
    scene.append_to_caption("z")
    sliderz = slider(bind=do_slider, max=1000, min = -1000, step=1, value=sph.pos.z, 
                     id=f'{sph.idx}-pos-z', length=SLIDER_LEN)
    scene.append_to_caption("velocity: x")
    slidervx = slider(bind=do_slider, max=10, min = -10, step=1, value=celestial.velocity.x, 
                     id=f'{sph.idx}-vel-x', length=SLIDER_LEN)
    scene.append_to_caption("y")
    slidervy = slider(bind=do_slider, max=10, min = -10, step=1, value=celestial.velocity.y, 
                     id=f'{sph.idx}-vel-y', length=SLIDER_LEN)
    scene.append_to_caption("z")
    slidervz = slider(bind=do_slider, max=10, min = -10, step=1, value=celestial.velocity.z, 
                     id=f'{sph.idx}-pos-z', length=SLIDER_LEN)
    celestial.wt = wtext(text=f"({celestial.pos.__str__().strip('<>')}) {celestial.vel}")
    randomizeButton = button(bind=randomize, text="random", id=f"randbutton-{i}")
    scene.append_to_caption('\n\n')
    celestials.append(celestial)
    sliders.extend([sliderx, slidery, sliderz, slidervx, slidervy, slidervz, randomizeButton])

goButton = button(bind=toggle_simulation, text="GO", background=color.green)
gravToggleButton = button(bind=toggle_grav, text="Gravity arrows are ON", background=color.yellow)
velToggleButton = button(bind=toggle_vel, text="Velocity arrows are ON", background=color.yellow)
lablToggleButton = button(bind=toggle_labels, text="Labels are ON", background=color.yellow)

#timeSlider = slider(bind=

celestials[0].pos = vec(-500, 0, 0)
celestials[1].pos = vec(700, 0, 0)
celestials[2].pos = vec(200, 1280, 0)


#evt = scene.waitfor('draw_complete')

#print([x.__dict__ for x in scene.objects])

while True:
    rate(50)
    dt = 1.5
    do_input()
    for c in celestials:
        calc_gravity(c, celestials)
        #print(f"{c.name} pos={c.pos} vel={c.vel} grav={c.total_grav}")
    if SIMULATION_START:
        for s in celestials:
            s.vel = s.vel + (s.total_grav/s.mass) * dt
            s.pos = s.pos + s.vel * dt
            print(f"{s.name} pos={s.pos} vel={s.vel} grav={s.total_grav}")
