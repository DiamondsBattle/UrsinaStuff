import discord_rpc
import time
from ursina import *


class DiscordRpc:
    def __init__(self, client_id, details, large_image, large_image_text='',
                 small_image='', small_image_text='',
                 party_id='', party_size='',
                 join='', spectate='', match='',
                 log=False):
        self.client_id = client_id
        self.details = details
        self.start = time.time()
        self.large_image = large_image
        self.large_image_text = large_image_text
        self.small_image = small_image
        self.small_image_text = small_image
        self.log = log
        self.callbacks = {
            'ready': self.readyCallback,
            'disconnected': self.disconnectedCallback,
            'error': self.errorCallback,
        }

        self.start = time.time()
        self.callable = True

        discord_rpc.initialize(self.client_id, callbacks=self.callbacks, log=False)

    def readyCallback(self, current_user):
        print(f'User {current_user}')

    def disconnectedCallback(self, codeno, codemsg):
        print(f'Disconnected from the DiscordRPC ({codeno} : {codemsg})')

    def errorCallback(self, errno, errmsg):
        print(f'An error occurred ({errno} : {errmsg})')

    def stop(self):
        discord_rpc.shutdown()

    def update(self):
        if not self.callable:
            return
        self.callable = False
        discord_rpc.update_presence(
            **{
                'state': 'DiamondsBattle',
                'details': self.details,
                'start_timestamp': self.start,
                'end_timestamp': self.start + 1000,
                'large_image_key': self.large_image,
                'large_image_text': 'Balistic Launcher 1.12.2',
                'small_image_key': self.small_image,
                'small_image_text': '',
                'party_id': '',
                'party_size': '',
                'join': '',
                'spectate': '',
                'match': '',
            }
        )

        discord_rpc.update_connection()
        invoke(discord_rpc.run_callbacks, delay=2)
        invoke(setattr, self, 'callable', True, delay=2)


if __name__ == '__main__':
    app = Ursina()
    conn = DiscordRpc(client_id='764881010416287756', details='Dans le lobby', large_image='logo')


    def update():
        conn.update()


    app.run()
