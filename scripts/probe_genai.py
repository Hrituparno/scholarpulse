import importlib

names = ['google.genai','google.generativeai','google']
for n in names:
    try:
        m = importlib.import_module(n)
        print('MODULE', n)
        print('file:', getattr(m, '__file__', 'builtin'))
        print('version:', getattr(m,'__version__', getattr(m,'VERSION', 'unknown')))
        attrs = sorted([a for a in dir(m) if not a.startswith('_')])
        print('attrs sample:', attrs[:60])
        for candidate in ['generate_text','chat','Client','configure','create','TextGenerationModel','TextServiceClient']:
            found = any(candidate == a or candidate in a for a in attrs)
            print('has', candidate, found)
        print('\n')
    except Exception as e:
        print('NO MODULE', n, '->', e)
