from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Load T5 directly (no pipeline dependency)
tokenizer = AutoTokenizer.from_pretrained("t5-small")
model = AutoModelForSeq2SeqLM.from_pretrained("t5-small")

def medical_summary(text):

    text = text[:2000] # limiting size

    prompt = "summarize medical case: " + text

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=512
    ) # Converting text to model tokens

    outputs = model.generate(
        inputs["input_ids"],
        max_length=150,
        min_length=40,
        num_beams=4,
        no_repeat_ngram_size=2
    ) #Generating summary

    summary = tokenizer.decode(outputs[0], skip_special_tokens=True) # Decoding the generated tokens to text

    return summary
