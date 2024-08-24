
# Eunoia - Open Domain Chitchat System

**Eunoia** is a sophisticated open-domain conversational AI system designed for seamless, human-like interaction. It combines state-of-the-art natural language understanding (NLU) using **BERT** and **RoBERTa LLMs**, an advanced confirmation mechanism powered by the **XGBoost classification algorithm** with feature engineering, and robust dialogue state tracking (DST) for managing multi-turn conversations.

## Key Features
- **Natural Language Understanding (NLU)**: Leverages powerful LLMs like **BERT** and **RoBERTa** for joint intent detection and slot filling.
- **Confirmation Server with XGBoost**: Utilizes XGBoost with feature engineering to validate user actions and ensure decision accuracy.
- **Dialogue State Tracking (DST)**: Manages conversation flow by tracking the context across multiple dialogue turns.
- **API Integration**: Dynamically interacts with external systems for real-time responses and actions.

---

### Natural Language Understanding (NLU)
The **Eunoia** system leverages advanced pre-trained **BERT** and **RoBERTa** large language models (LLMs) for joint intent detection and slot filling. The **RoBERTa** model is fine-tuned for the dual task of intent classification and slot label prediction, ensuring accurate and context-aware language understanding.

- **BERT/ RoBERTa Models**: The system utilizes **RoBERTa (xlm-roberta-large)** for multilingual support, capable of handling diverse linguistic inputs. The model is fine-tuned to perform:
  - **Intent Detection**: Classifying the user’s intent from a predefined set of intent labels.
  - **Slot Filling**: Extracting relevant entities (slots) from user input in a single joint model for improved performance.
  
- **Fine-Tuning**: The model is further fine-tuned using task-specific data to enhance its performance on intent detection and slot filling tasks. The system also incorporates **class weighting** during training to handle imbalanced datasets effectively.

- **Tokenizer**: A **RoBERTa tokenizer** is used to convert input text into tokens that the model can process, ensuring proper handling of different languages and subword tokenization.

This joint approach allows the system to efficiently handle natural language inputs, extracting both intents and entities in a single pass, optimizing both accuracy and speed in open-domain conversations.

---

### Confirmation Module with XGBoost
The **Confirmation Server** in the **Eunoia** system is powered by the **XGBoost classification algorithm**, incorporating advanced **feature engineering** techniques to ensure robust validation and decision-making.

- **XGBoost Classifier**: The system uses **XGBoost** to classify and confirm actions based on user input. XGBoost is a high-performance, scalable machine learning algorithm that is well-suited for classification tasks involving complex decision boundaries.
  
- **Feature Engineering**: Several engineered features are incorporated to improve model accuracy, including:
  - **Interaction Features**: Combining softmax and normalized intent probabilities to create interaction terms.
  - **Polynomial Features**: Generating higher-order features to capture nonlinear relationships between the intents and actions.
  
- **Threshold Optimization**: XGBoost’s output probabilities are fine-tuned using optimized thresholds, ensuring accurate classification in real-world use cases.

- **Oversampling and Class Balancing**: Techniques like **SMOTE** (Synthetic Minority Oversampling Technique) are used to balance the class distribution, ensuring the model is robust against imbalanced data.

This feature-rich confirmation module ensures that user actions are thoroughly validated, minimizing false positives and enhancing the reliability of the conversational system.

---

### Dialogue State Tracking (DST)
The **Eunoia** system includes a robust **Dialogue State Tracking (DST)** module to manage and track the context of the conversation across multiple turns, ensuring that the chatbot maintains continuity and responds coherently to user inputs over time. The system interacts with a database for storing and retrieving conversation states, slots, and other contextual information.

- **Slot Management**: The system handles slot filling by extracting relevant entities from user input and storing them in a structured format. This information is used to maintain the current state of the conversation and determine which actions to take next.

- **Intent Recognition and State Tracking**: The **DST** module relies on detected intents and associated slots to manage dialogue state transitions. The tracked state is used to maintain the flow of the conversation, enabling multi-turn interactions where user context is remembered.

- **Database Integration**: The system connects to a PostgreSQL database to persist conversation data. This includes storing user requests, conversation IDs, slot information, and other relevant dialogue data that can be retrieved and updated during the interaction.

- **Language Detection**: The **DST** module includes functionality for language detection to adapt to multilingual inputs, ensuring accurate processing of both English and Persian texts.

- **Turn Management**: The **DST** system assigns turn IDs to manage the flow of conversation, ensuring each user request is processed sequentially and associated with the correct context.

This dynamic state tracking enables the **Eunoia** system to handle complex, multi-turn dialogues, ensuring that user context is maintained throughout the conversation for more coherent and relevant responses.

---

### Results

The performance of the **Eunoia** system’s Dialogue State Tracking (DST) module is evaluated using several important metrics:

- **Joint Goal Accuracy (JGA)**:  
  The proportion of dialogue turns where both the intent and the slots are correctly identified. This is a stricter measure of the system's performance, as both components must be correct for the turn to be counted as successful.

- **Flexible Goal Accuracy (FGA)**:  
  The proportion of turns where either the intent or the slots are correctly identified. This metric is more lenient, providing insight into partial successes where at least one of the key components is correct.

- **Average Goal Accuracy**:  
  A measure of the system's overall accuracy, averaged across all turns and components.

- **Status Accuracy**:  
  This evaluates the correctness of status updates within the conversation, which reflects how well the system tracks the state over time.

These results demonstrate the effectiveness of the **DST** module in maintaining and understanding dialogue context, while the combination of **NLU** and **Confirmation** ensures high accuracy in intent detection and decision validation.
