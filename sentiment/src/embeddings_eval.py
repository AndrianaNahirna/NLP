def print_neighbors(word, model_w2v, model_ft, topn=5):
    """Виводить найближчих сусідів для обох моделей"""
    print(f"Сусіди для слова: '{word}'")
    
    try:
        w2v_sim = [f"{w} ({s:.2f})" for w, s in model_w2v.wv.most_similar(word, topn=topn)]
        print(f"Word2Vec: {', '.join(w2v_sim)}")
    except KeyError:
        print("Word2Vec: [OOV]")
        
    try:
        ft_sim = [f"{w} ({s:.2f})" for w, s in model_ft.wv.most_similar(word, topn=topn)]
        print(f"FastText: {', '.join(ft_sim)}")
    except KeyError:
        print("FastText: [OOV]")