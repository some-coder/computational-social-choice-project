import seaborn as sns

from world import World

def main():
    world: object = World()
    world.run()
    world.save()
    world.plot()

if __name__ == main:
    main()
