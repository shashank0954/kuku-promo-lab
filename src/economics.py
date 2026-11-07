"""Transparent, editable estimates; actual invoice = provider usage × applicable rates."""
RATES={'gemini-2.5-flash':(.30,2.50),'gpt-4o-mini':(.15,.60),'gpt-4o':(2.50,10),
       'gemini-2.5-pro':(1.25,10),'claude-sonnet-4-5':(3,15),'claude-haiku-4-5':(1,5)}

def cost(input_tokens,output_tokens,input_rate,output_rate):
    return round((input_tokens*input_rate+output_tokens*output_rate)/1_000_000,6)

def estimate(shortlist=8,tokens_each=1800,output_each=160,input_rate=.30,output_rate=2.50,
             raw_tokens=200000,naive_passes=3,naive_output=10000):
    return {'hybrid_usd':cost(shortlist*tokens_each,shortlist*output_each,input_rate,output_rate),
            'naive_same_model_usd':cost(raw_tokens*naive_passes,naive_output,input_rate,output_rate),
            'naive_premium_usd':cost(raw_tokens*naive_passes,naive_output,2.50,10),
            'input_tokens_estimated':shortlist*tokens_each,'output_tokens_estimated':shortlist*output_each}
