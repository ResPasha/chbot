import telepot
import config

def singleton(class_):
    instances = {}
    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance

@singleton
class Bot(telepot.Bot):
    def __init__(self, queue=None, url=None):
        super().__init__(config.TOKEN)
        self.queue = queue
        if self.queue:
            self.bot.setWebhook(url)

    def message_loop(self,
                     callback=None,
                     relax=0.1,
                     timeout=20,
                     source=None,
                     ordered=True,
                     maxhold=3,
                     run_forever=False):
        super().message_loop(callback=callback,
                             relax=relax,
                             timeout=timeout,
                             source=self.queue,
                             ordered=ordered,
                             maxhold=maxhold,
                             run_forever=(not self.queue))
