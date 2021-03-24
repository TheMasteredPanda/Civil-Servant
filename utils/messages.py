from discord import Embed

def send_simple_embed(author, target, message):
    embed = Embed(title="Message", description=message)
    #embed.add_field(name="Message", value=message)
    embed.set_footer(text='By {} for {}'.format(author.name, target.name))
    return embed
