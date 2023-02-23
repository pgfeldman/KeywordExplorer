from keyword_explorer.tkUtils.GPT3GeneratorFrame import GPT3GeneratorFrame, GPT3GeneratorSettings

class GPTContextSettings(GPT3GeneratorSettings):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class GPTContextFrame(GPT3GeneratorFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)