import re

def get_sender_vc(ctx):
    try:
        return ctx.author.voice.channel
    except:
        return None

def is_sender_same_vc_as_bot(ctx):
    try:
        return ctx.author.voice.channel == ctx.voice_client.channel
    except:
        return False

async def connect_vc_of_author(ctx):
    new_vc = ctx.author.voice.channel
    current_vc = ctx.voice_client
    if is_sender_same_vc_as_bot(ctx):
        return ctx.voice_client
    if current_vc:
        await current_vc.move_to(new_vc)
    else:
        await new_vc.connect()
    return ctx.voice_client
    
def check_text(text):
    if "http" in text:
        return False

    if "```" in text:
        return False
    
    if not text[:1].isalnum():
        return False

    return True
