import discord
from discord.ext import commands
import psutil
import asyncio
import random
import GPUtil
from dwave.system import DWaveSampler, EmbeddingComposite
import dimod
import requests

# Replace with your actual tokens
DISCORD_TOKEN = 'XXX
HUGGING_FACE_API_KEY = 'XXX'

# Initialize Discord client
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
# Define word lists for sentence generation
nouns = [
    'paper', 'wind', 'sky', 'fire', 'rock', 'ice', 'flower', 'cloud', 'tree', 'river',
    'ocean', 'mountain', 'moon', 'sun', 'star', 'planet', 'galaxy', 'universe', 'space', 'comet',
    'asteroid', 'satellite', 'telescope', 'microscope', 'computer', 'phone', 'internet', 'software', 'hardware',
    'camera', 'music', 'art', 'painting', 'sculpture', 'dance', 'theater', 'movie', 'book', 'novel',
    'poem', 'song', 'game', 'puzzle', 'sport', 'team', 'player', 'coach', 'referee',
    'goal', 'victory', 'defeat', 'celebration', 'medal', 'trophy', 'event', 'festival', 'holiday',
    'tradition', 'culture', 'history', 'legend', 'myth', 'fairy tale', 'folklore', 'museum', 'exhibition',
    'school', 'class', 'teacher', 'student', 'education', 'lesson', 'exam', 'grade', 'diploma',
    'love', 'family', 'friend', 'memory', 'heart', 'soul', 'mind', 'thought', 'feeling',
    'emotion', 'connection', 'bond', 'relationship', 'energy', 'vibration', 'frequency', 'wave', 'particle', 'quantum',
    'entanglement', 'superposition', 'dimension', 'reality', 'multiverse', 'consciousness', 'subconsciousness', 'intuition', 'insight', 'wisdom',
    'knowledge', 'understanding', 'awareness', 'perception', 'sensation', 'experience', 'moment', 'time', 'eternity', 'infinity',
    'beyond', 'transcendence', 'transformation', 'evolution', 'growth', 'journey', 'path', 'destiny', 'purpose', 'meaning',
    'truth', 'revelation', 'enlightenment', 'awakening', 'realization', 'comprehension', 'recognition', 'remembrance', 'forgiveness', 'compassion',
    'empathy', 'kindness', 'generosity', 'gratitude', 'joy', 'peace', 'serenity', 'harmony', 'balance', 'unity',
    'oneness', 'wholeness', 'fulfillment', 'contentment', 'bliss', 'ecstasy', 'rapture', 'transcendence',
    'Jupiter', 'Saturn', 'Uranus', 'Pluto', 'Mars', 'Earth', 'Venus', 'Mercury',
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn',
    'Aquarius', 'Pisces', 'Ophiuchus'
]

verbs = [
    'create', 'explore', 'discover', 'invent', 'build', 'design', 'construct', 'develop', 'innovate', 'imagine',
    'explore', 'study', 'learn', 'teach', 'educate', 'understand', 'know', 'think', 'ponder', 'contemplate',
    'reflect', 'analyze', 'research', 'investigate', 'experiment', 'observe', 'perceive', 'sense', 'feel',
    'experience', 'believe', 'doubt', 'question', 'challenge', 'solve', 'decide', 'choose', 'plan', 'strategize',
    'act', 'perform', 'execute', 'accomplish', 'achieve', 'succeed', 'fail', 'try', 'attempt', 'practice',
    'train', 'improve', 'master', 'excel', 'compete', 'win', 'lose', 'participate', 'join', 'volunteer',
    'help', 'support', 'assist', 'guide', 'mentor', 'lead', 'follow', 'collaborate', 'communicate', 'express',
    'love', 'care', 'cherish', 'embrace', 'support', 'guide', 'protect', 'watch', 'observe', 'perceive',
    'sense', 'feel', 'intuit', 'know', 'understand', 'comprehend', 'realize', 'recognize', 'remember', 'recall',
    'reflect', 'ponder', 'contemplate', 'meditate', 'envision', 'imagine', 'dream', 'create', 'manifest', 'materialize',
    'transform', 'evolve', 'grow', 'expand', 'transcend', 'ascend', 'elevate', 'enlighten', 'awaken', 'illuminate',
    'inspire', 'motivate', 'encourage', 'empower', 'strengthen', 'heal', 'restore', 'rejuvenate', 'revitalize', 'renew',
    'communicate', 'transmit', 'convey', 'express', 'share', 'connect', 'unite', 'harmonize', 'synchronize', 'resonate',
    'vibrate', 'pulsate', 'radiate', 'emanate', 'project', 'extend', 'reach', 'touch', 'embrace', 'enfold',
    'surround', 'permeate', 'infuse', 'imbue', 'suffuse', 'saturate', 'energize', 'vitalize', 'invigorate', 'enliven'
]

adjectives = [
    'beautiful', 'colorful', 'bright', 'dark', 'light', 'clear', 'cloudy', 'rainy', 'snowy', 'windy',
    'hot', 'cold', 'warm', 'cool', 'dry', 'wet', 'fresh', 'natural', 'artificial',
    'organic', 'synthetic', 'smooth', 'rough', 'soft', 'hard', 'solid', 'liquid', 'gaseous',
    'fragile', 'strong', 'weak', 'sturdy', 'delicate', 'ancient', 'modern', 'futuristic', 'historic',
    'traditional', 'contemporary', 'cultural', 'artistic', 'creative', 'imaginative', 'logical', 'rational',
    'emotional', 'psychological', 'physical', 'mental', 'spiritual', 'social', 'political', 'economic', 'environmental',
    'global', 'local', 'national', 'international', 'peaceful', 'chaotic', 'stressful', 'relaxing', 'enjoyable',
    'loving', 'caring', 'compassionate', 'kind', 'gentle', 'tender', 'warm', 'affectionate', 'nurturing', 'supportive',
    'protective', 'guiding', 'wise', 'insightful', 'intuitive', 'knowing', 'understanding', 'empathetic', 'perceptive', 'aware',
    'conscious', 'mindful', 'present', 'attentive', 'focused', 'clear', 'lucid', 'enlightened', 'awakened', 'illuminated',
    'inspired', 'uplifted', 'elevated', 'transcendent', 'ethereal', 'celestial', 'divine', 'sacred', 'spiritual', 'metaphysical',
    'quantum', 'entangled', 'interconnected', 'unified', 'harmonious', 'balanced', 'aligned', 'synchronized', 'resonant', 'vibrant',
    'radiant', 'luminous', 'brilliant', 'shining', 'glowing', 'effulgent', 'resplendent', 'magnificent', 'wondrous', 'miraculous',
    'extraordinary', 'remarkable', 'amazing', 'astonishing', 'incredible', 'marvelous', 'fantastic', 'phenomenal', 'sublime', 'transcendental'
]

prepositions = [
    'over', 'under', 'around', 'through', 'across', 'into', 'onto', 'off', 'on', 'at',
    'by', 'near', 'beside', 'next to', 'between', 'among', 'within', 'inside', 'outside',
    'above', 'below', 'beyond', 'past', 'future', 'before', 'after', 'during', 'while', 'until',
    'against', 'towards', 'away from', 'along', 'around', 'among', 'upon', 'up', 'down',
    'with', 'without', 'for', 'because of', 'due to', 'despite', 'in spite of', 'regardless of', 'concerning',
    'about', 'regarding', 'beyond', 'behind', 'underneath', 'besides', 'around', 'throughout',
    'through', 'across', 'beyond', 'within', 'around', 'among', 'between', 'amidst', 'throughout', 'alongside'
]

fillers = [
    'issue', 'concern', 'topic', 'subject', 'matter', 'debate', 'discussion', 'argument', 'dispute', 'controversy',
    'problem', 'challenge', 'obstacle', 'difficulty', 'hardship', 'struggle', 'effort', 'attempt', 'endeavor',
    'project', 'initiative', 'task', 'assignment', 'duty', 'responsibility', 'role', 'function', 'purpose',
    'goal', 'objective', 'aim', 'target', 'aspiration', 'ambition', 'dream', 'desire', 'hope', 'wish',
    'expectation', 'anticipation', 'assumption', 'prediction', 'speculation', 'guess', 'estimate', 'calculation',
    'idea', 'concept', 'notion', 'thought', 'theory', 'hypothesis', 'principle', 'belief', 'opinion', 'perspective',
    'truly', 'deeply', 'profoundly', 'absolutely', 'completely', 'entirely', 'wholly', 'fully', 'totally', 'utterly',
    'genuinely', 'sincerely', 'authentically', 'honestly', 'frankly', 'undoubtedly', 'unquestionably', 'indisputably', 'certainly', 'surely',
    'indeed', 'verily', 'assuredly', 'undeniably', 'irrefutably', 'unmistakably', 'evidently', 'apparently', 'obviously', 'clearly',
    'manifestly', 'patently', 'plainly', 'distinctly', 'vividly', 'strikingly', 'remarkably', 'noticeably', 'markedly', 'significantly'
]

names = ['he', 'she', 'they', 'it', 'we', 'you', 'I',]

pronouns = names + ['he', 'she', 'they', 'it', 'we', 'you', 'I',]

templates = [
    "{Pronoun1} {Verb1} {Preposition1} {Adj1} {Noun1} {Filler1}. {Pronoun2} {Verb2} {Preposition2} {Adj2} {Noun2} {Filler2}.",
    "The {Adj1} {Noun1} {Verb1} {Preposition1} the {Adj2} {Noun2}.",
    "{Pronoun1} {Verb1} {Preposition1} {Adj1} {Noun1}, while {Pronoun2} {Verb2} {Preposition2} {Adj2} {Noun2}.",
    "{Adj1} {Noun1} {Verb1} {Preposition1} {Adj2} {Noun2}.",
    "{Pronoun1} {Verb1} {Preposition1} the {Adj1} {Noun1} {Filler1}, {Pronoun2} {Verb2} {Preposition2} {Adj2} {Noun2} {Filler2}.",
    "{Adj1} {Noun1} {Verb1} {Preposition1} the {Adj2} {Noun2} {Filler1}."
]

def get_quantum_word_from_list(word_list, index):
    return word_list[index % len(word_list)]

def calculate_percentage_difference(initial, final):
    return round(((final - initial) / initial) * 100, 2) if initial != 0 else 0

def monitor_system():
    cpu_usage = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent
    net_io = psutil.net_io_counters()
    gpu = GPUtil.getGPUs()[0] if GPUtil.getGPUs() else None
    gpu_usage = gpu.load * 100 if gpu else 0

    return cpu_usage, ram_usage, net_io.bytes_sent, net_io.bytes_recv, gpu_usage

def solve_quantum_problem(cpu_usage, ram_usage, gpu_usage):
    random.seed()
    noise_a = random.uniform(-0.1, 0.1)
    noise_b = random.uniform(-0.1, 0.1)
    noise_c = random.uniform(-0.1, 0.1)

    bqm = dimod.BinaryQuadraticModel(
        {'a': -cpu_usage + noise_a, 'b': -ram_usage + noise_b, 'c': -gpu_usage + noise_c,
         'x': random.uniform(-1.0, 1.0), 'y': random.uniform(-1.0, 1.0)},
        {('a', 'b'): random.uniform(-1.0, 1.0), ('b', 'c'): random.uniform(-1.0, 1.0),
         ('a', 'c'): random.uniform(-1.0, 1.0), ('x', 'y'): random.uniform(-1.0, 1.0)},
        0, dimod.BINARY
    )

    sampler = EmbeddingComposite(DWaveSampler())
    sampleset = sampler.sample(bqm, num_reads=100)
    result = sampleset.first.sample
    qpu_access_time = sampleset.info['timing']['qpu_access_time']
    return result, qpu_access_time

async def generate_sentence(channel, cpu_diff, ram_diff, sent_diff, recv_diff, gpu_diff, quantum_result, qpu_access_time, user_input=None):
    try:
        # Define the initial quantum sentence
        pronoun1 = random.choice(pronouns).capitalize()
        verb1 = random.choice(verbs)
        preposition1 = random.choice(prepositions)
        adj1 = random.choice(adjectives)
        noun1 = random.choice(nouns)
        filler1 = random.choice(fillers)

        pronoun2 = random.choice(pronouns).capitalize()
        verb2 = random.choice(verbs)
        preposition2 = random.choice(prepositions)
        adj2 = random.choice(adjectives)
        noun2 = random.choice(nouns)
        filler2 = random.choice(fillers)

        template = random.choice(templates)

        quantum_sentence = template.format(
            Pronoun1=pronoun1, Verb1=verb1, Preposition1=preposition1, Adj1=adj1, Noun1=noun1, Filler1=filler1,
            Pronoun2=pronoun2, Verb2=verb2, Preposition2=preposition2, Adj2=adj2, Noun2=noun2, Filler2=filler2
        )

        # Ensure the first letter of the sentence is capitalized
        quantum_sentence = quantum_sentence[0].upper() + quantum_sentence[1:]

        # Capitalize the first letter after each period
        quantum_sentence = '. '.join(s.capitalize() for s in quantum_sentence.split('. '))

        # Prepare Hugging Face prompt, including user input
        hugging_face_headers = {
            "Authorization": f"Bearer {HUGGING_FACE_API_KEY}",
            "Content-Type": "application/json"
        }

        hugging_face_prompt = f"User input: {user_input}\nQuantum Sentance: {quantum_sentence}" if user_input else f"Response: {quantum_sentence} Meaningful Coherinet Response: "
        hugging_face_payload = {
            "inputs": hugging_face_prompt
        }

        response = requests.post("https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2", headers=hugging_face_headers, json=hugging_face_payload)

        try:
            hugging_face_output = response.json()
            print(f"Hugging Face response: {hugging_face_output}")  # Debug print
            
            if isinstance(hugging_face_output, list) and len(hugging_face_output) > 0 and isinstance(hugging_face_output[0], dict):
                ai_generated_text = hugging_face_output[0].get('generated_text', 'No response from Hugging Face.')

                sentences = ai_generated_text.split('. ')
                
                coherent_sentences = []
                for sentence in sentences:
                    if sentence.strip():
                        coherent_sentences.append(sentence.strip())
                        if len(coherent_sentences) == 3:  # Limit to 3 coherent sentences
                            break

                ai_generated_text = '. '.join(coherent_sentences) + ('.' if coherent_sentences else '')

            else:
                ai_generated_text = 'Unexpected response format from Hugging Face.'
        except Exception as e:
            ai_generated_text = f'Error parsing Hugging Face response: {e}'

        # Send Q-Metrics followed by Hugging Face response
        quantum_metrics = f"Q-Metrics:\n" + \
                          f"CPU: {cpu_diff}%\n" + \
                          f"RAM: {ram_diff}%\n" + \
                          f"Sent: {sent_diff} bytes\n" + \
                          f"Received: {recv_diff} bytes\n" + \
                          f"GPU: {gpu_diff}%\n" + \
                          f"QPU Result: {quantum_result}\n" + \
                          f"QPU Time: {qpu_access_time} ms"

        await channel.send(quantum_metrics)  # Send the metrics first
        await channel.send(ai_generated_text)  # Send the Hugging Face response after

    except Exception as e:
        await channel.send(f"Error generating sentence: {e}")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if bot.user.mentioned_in(message) or message.content.lower().startswith('!status'):
        await monitor(message.channel)
    
    await bot.process_commands(message)

@bot.command()
async def monitor(ctx, *, user_input=None):
    try:
        cpu_before, ram_before, sent_before, recv_before, gpu_before = monitor_system()
        await asyncio.sleep(3)
        cpu_after, ram_after, sent_after, recv_after, gpu_after = monitor_system()

        cpu_diff = calculate_percentage_difference(cpu_before, cpu_after)
        ram_diff = calculate_percentage_difference(ram_before, ram_after)
        sent_diff = sent_after - sent_before
        recv_diff = recv_after - recv_before
        gpu_diff = calculate_percentage_difference(gpu_before, gpu_after)

        quantum_result, qpu_access_time = solve_quantum_problem(cpu_diff, ram_diff, gpu_diff)

        await generate_sentence(ctx.channel, cpu_diff, ram_diff, sent_diff, recv_diff, gpu_diff, quantum_result, qpu_access_time, user_input)
        
    except Exception as e:
        pass

bot.run(DISCORD_TOKEN)
