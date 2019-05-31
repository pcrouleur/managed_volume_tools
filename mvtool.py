import managed_volumes
import click

@click.command()
@click.option(
     '--managed_volume', '-m',
     help='Your Rubrik Password')
def cli(managed_volume):
    print('Managed Volumes Setup Tool')
    print("The managed volume is {}.".format(managed_volume))
    print('#' * 80)
    if not managed_volume:
        managed_volume = click.prompt('Please enter a managed volume name', type=str)
        click.echo("The managed volume name entered is {}.".format(managed_volume))

    mv = managed_volumes.ManagedVolume(managed_volume)
    mv.cluster_info()
    print("CONNECTED TO: {}".format(mv.cluster['name']))
    # print("The managed volume name is {}.\n".format(mv.name))

    if mv.data:
        print("The managed volume {} exists and the managed volume id is {}.".format(mv.name, mv.id))
    else:
        while True:
            print("The managed volume {} does not exist.".format(managed_volume))
            click.confirm('Would you like to try another managed volume?', abort=True)
            managed_volume = click.prompt('Please enter a managed volume name', type=str)
            mv = managed_volumes.ManagedVolume(managed_volume)
            if mv.data:
                break

    mv.print_mounts()
    mv.print_snapshot_cmds()
    mv.print_rman_channels()

    print("isWritable is {}".format(mv.isWritable))
    if mv.isWritable:
        snapshot_state = "Writable"
    else:
        snapshot_state = "Read Only"

    print("The current state of the {} managed volume is {} and the managed volume is {}".format(mv.name, mv.state,
                                                                                                 snapshot_state))
    exit(0)

    
if __name__ == "__main__":
    cli()