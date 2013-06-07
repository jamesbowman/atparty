import random
import sys
import gameduino.prep as gdprep
import gameduino as gd
import Image
import math

# import Box2D.b2 as b2
import Box2D as box2d

def aball(world, x, y, r):
    sd=box2d.b2PolygonShape()
    sd.SetAsBox(r, r)
    sd.restitution = 0.05
    
    bd=box2d.b2BodyDef()
    bd.position = (x, y)
    body = world.CreateDynamicBody(position=(x,y))
    # body = world.CreateBody(bd)
    groundBoxFixture=box2d.b2FixtureDef(shape=sd)
    body.CreateFixture(groundBoxFixture)
    # body.ResetMassData()
    return body

def abox(world, x, y, w, h):
    sd=box2d.b2PolygonShape()
    sd.SetAsBox(w, h)
    sd.density = 2.0
    sd.friction = 0.3
    sd.restitution = 0.2
    
    bd=box2d.b2BodyDef()
    bd.position = (x, y)
    body = world.CreateDynamicBody(position=(x,y))
    # body = world.CreateBody(bd)
    groundBoxFixture=box2d.b2FixtureDef(shape=sd)
    body.CreateFixture(groundBoxFixture)
    body.ResetMassData()
    body.inertia = .02
    body.mass = 1
    return body

def blk6x8(world):
    sz = (20,20)
    for i in range(6):
        for j in range(8):
            w = 0.5 * (sz[0] - 2) / 60.
            h = 0.5 * (sz[1] - 2) / 60.
            he = h * 1.01
            x = -1.5 + i / 2.
            y = he + 2*he * j
            b = abox(world, x, y, w, h)
            yield b

def runsim(GD, locs, seed, mapgen, vel, frames, slowmo = 1):
    random.seed(seed)
    # Define the size of the world. Simulation will still work
    # if bodies reach the end of the world, but it will be slower.
    worldAABB=box2d.b2AABB()
    worldAABB.lowerBound = (-100, -100)
    worldAABB.upperBound = ( 100,  100)

    # Define the gravity vector.
    gravity = box2d.b2Vec2(0, -10)
     
    # Do we want to let bodies sleep?
    doSleep = False
     
    # Construct a world object, which will hold and simulate the rigid bodies.
    world = box2d.b2World(gravity, doSleep)

    if 1:
        sd=box2d.b2PolygonShape()
        sd.SetAsBox(50.0, 10.0)
        
        bd=box2d.b2BodyDef()
        bd.position = (0.0, -10.0)
        ground = world.CreateBody(bd)
        groundBoxFixture=box2d.b2FixtureDef(shape=sd)
        ground.CreateFixture(groundBoxFixture)
    else:
        # Define the ground body.
        groundBodyDef = box2d.b2BodyDef()
        groundBodyDef.position = [0, -10]
         
        # Call the body factory which allocates memory for the ground body
        # from a pool and creates the ground box shape (also from a pool).
        # The body is also added to the world.
        groundBody = world.CreateBody(groundBodyDef)
         
        # Define the ground box shape.
        groundShapeDef = box2d.b2PolygonShape()
         
        # The extents are the half-widths of the box.
        groundShapeDef.SetAsBox(50, 10)
         
        # Add the ground shape to the ground body.
        help(groundBody)
        groundBody.CreateShape(groundShapeDef)
     
    bodies = [b for b in mapgen(world)]

    # Prepare for simulation. Typically we use a time step of 1/60 of a
    # second (60Hz) and 10 velocity/8 position iterations. This provides a 
    # high quality simulation in most game scenarios.
    timeStep = 1.0 / 60
    vel_iters, pos_iters = 10, 8
    vel_iters, pos_iters = 1000, 1000
     
    # class MyContactListener(box2d.b2ContactListener):
    #     def __init__(self):
    #         self.contact = False
    #         super(MyContactListener, self).__init__()
    #     def Add(self, point):
    #         if box2d.b2CircleShape in (type(point.shape1), type(point.shape2)):
    #             self.contact = True
    # contactListener = MyContactListener()
    # world.SetContactListener(contactListener)

    def bodxy(b):
        x,y = int((220 + 60 * (b.position.x + ox))), int((270 - 60 * (b.position.y + oy)))
        return x - 16,y-16

    bullet = None
    yground = 265
    time = 0.0

    for f in range(400):
        print 'f', f, bodies[0].position
        world.Step(timeStep, vel_iters, pos_iters)
        for i,b in enumerate(bodies):
            (ox, oy) = (0,0)
            x,y = bodxy(b)
            a = (f/4) % 120
            a = int(30 * b.angle / (math.pi / 2)) % 120
            fr = a % 30
            rot = (a/30) % 4
            tab = ([0,1,2,3],
                   [1,3,0,2],
                   [3,2,1,0],
                   [2,0,3,1])[rot]
            for j in range(4):
                frame,pal = locs[4*fr+tab[j]]
                GD.sprite(4 * i + j, x + (16 * (j % 2)), y + 16 * (j / 2), frame, pal,
                          [0,3,6,5][rot])
        if bullet:
            x,y = bodxy(bullet)
            GD.sprite(255, x + 8, y + 8, 63, 0)
        GD.sync_spr()
        GD.wait()
        time += timeStep
        if f == 60:
            bullet = aball(world, -4, 0, .1)
            bullet.mass = 9
            bullet.linearVelocity = box2d.b2Vec2(8,4) * 1

from dna import loadspr
def blocks(GD):
    blk = Image.open("assets/block25.png")
    blks = Image.new("RGBA", (32, 32 * 30))
    for i in range(30):
        rblk = blk.rotate(3 * i)
        blks.paste(rblk, (0,32 * i))
    im = gdprep.palettize(blks, 16)
    im.save("out.png")
    hh = open("../../dna.h", "w")
    ir = gdprep.ImageRAM(hh)
    # ir.addsprites("sphere", (16,16), im, gdprep.PALETTE16A, (8,8))
    locs = loadspr(ir, im, (16, 16))
    sprpal = gdprep.getpal(im)
    GD.wrstr(gd.PALETTE16A, sprpal)
    GD.wr16(gd.RAM_PAL, gd.RGB(100,200,200))

    ball = gdprep.palettize(Image.open("assets/lighting00.png"), 256)
    ir.nxtpage = 63
    ir.addsprites("sphere", (16,16), ball, gdprep.PALETTE256A, (8,8))
    GD.wrstr(gd.RAM_SPRPAL, gdprep.getpal(ball))

    GD.wrstr(gd.RAM_SPRIMG, ir.used())

    runsim(GD, locs, 0x0003, blk6x8, 4.0, 120)
