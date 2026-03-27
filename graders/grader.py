def grade_action(action, state, last_response=None):
    category_match = 1.0 if action.category.lower() == state.correct_category.lower() else 0.0
    priority_match = 1.0 if action.priority.lower() == state.correct_priority.lower() else 0.0
    
    response_lower = action.response.lower()
    
    # Keyword scoring
    if state.expected_keywords:
        match_count = sum(1 for kw in state.expected_keywords if kw.lower() in response_lower)
        response_score = match_count / len(state.expected_keywords)
    else:
        response_score = 1.0
        
    reward = (
        0.4 * category_match +
        0.3 * priority_match +
        0.3 * response_score
    )
    
    # 🔥 Penalties
    if category_match == 0:
        reward -= 0.2
        
    if priority_match == 0:
        reward -= 0.1
        
    if not action.response.strip():
        reward -= 0.5
        
    if last_response and action.response == last_response:
        reward -= 0.2
        
    # 🔥 Tone bonus
    polite_words = ["sorry", "please", "assist", "help"]
    if any(word in response_lower for word in polite_words):
        reward += 0.1
        
    return float(max(0.0, min(1.0, reward)))
