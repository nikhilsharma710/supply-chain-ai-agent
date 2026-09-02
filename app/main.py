import uuid

from langchain_core.messages import HumanMessage

from app.agent.graph import agent

def main():
    '''Run the interactive CLI.'''

    print('Supply Chain AI Agent')
    print('Type \'exit\' or \'quit\' to stop.\n')

    config = {'configurable': {'thread_id': str(uuid.uuid4())}}

    while True:
        user_input = input('You: ').strip()

        if user_input.lower() in {'exit', 'quit'}:
            print('Goodbye!')
            break

        if not user_input:
            continue

        try:
            response = agent.invoke(
                {
                    'messages': [
                        HumanMessage(content=user_input)
                    ]
                },
                config
            )

            result = response['messages'][-1].content
            print(f'\nAgent: {result}\n')
            
        except Exception as e:
            print(f'\nError: {e}\n')

if __name__ == '__main__':
    main()