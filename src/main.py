import seaborn as sns

from world import World

def main():
    world: object = World()
    world.run()
    print(world.blockchain)
    world.save()
    world.plot()

main()
