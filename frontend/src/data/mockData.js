// Mock data for ChatGPT clone

export const mockConversations = [
  {
    id: '1',
    title: 'React Best Practices',
    created_at: '2025-07-15T10:30:00Z',
    updated_at: '2025-07-15T10:45:00Z'
  },
  {
    id: '2',
    title: 'Python Data Analysis',
    created_at: '2025-07-14T14:20:00Z',
    updated_at: '2025-07-14T14:35:00Z'
  },
  {
    id: '3',
    title: 'SQL Query Optimization',
    created_at: '2025-07-13T09:15:00Z',
    updated_at: '2025-07-13T09:30:00Z'
  }
];

export const mockMessages = {
  '1': [
    {
      id: 'm1',
      conversation_id: '1',
      role: 'user',
      content: 'What are some React best practices?',
      created_at: '2025-07-15T10:30:00Z'
    },
    {
      id: 'm2',
      conversation_id: '1',
      role: 'assistant',
      content: 'Here are some React best practices:\n\n1. **Component Structure**: Keep components small and focused on a single responsibility.\n\n2. **Use Functional Components**: Prefer functional components with hooks over class components.\n\n3. **State Management**: Use useState for local state and Context API or state management libraries for global state.\n\n4. **Props Validation**: Use PropTypes or TypeScript for type checking.\n\n5. **Avoid Inline Functions**: Define functions outside JSX to prevent unnecessary re-renders.\n\n6. **Use Keys Properly**: Always use unique keys in lists.\n\n7. **Lazy Loading**: Use React.lazy() for code splitting and better performance.',
      created_at: '2025-07-15T10:30:15Z'
    }
  ],
  '2': [
    {
      id: 'm3',
      conversation_id: '2',
      role: 'user',
      content: 'How do I analyze data with Python pandas?',
      created_at: '2025-07-14T14:20:00Z'
    },
    {
      id: 'm4',
      conversation_id: '2',
      role: 'assistant',
      content: 'Here\'s how to analyze data with pandas:\n\n1. **Import and Read Data**:\n```python\nimport pandas as pd\ndf = pd.read_csv(\'data.csv\')\n```\n\n2. **Basic Exploration**:\n- df.head() - View first rows\n- df.info() - Data types and null values\n- df.describe() - Statistical summary\n\n3. **Data Cleaning**:\n- df.dropna() - Remove null values\n- df.fillna(value) - Fill null values\n\n4. **Analysis**:\n- df.groupby(\'column\').mean()\n- df.sort_values(\'column\')\n- df.pivot_table()\n\n5. **Visualization**:\n- df.plot()\n- df.hist()',
      created_at: '2025-07-14T14:20:20Z'
    }
  ],
  '3': [
    {
      id: 'm5',
      conversation_id: '3',
      role: 'user',
      content: 'Give me tips for SQL query optimization',
      created_at: '2025-07-13T09:15:00Z'
    },
    {
      id: 'm6',
      conversation_id: '3',
      role: 'assistant',
      content: 'SQL Query Optimization Tips:\n\n1. **Indexing**: Create indexes on frequently queried columns\n```sql\nCREATE INDEX idx_user_email ON users(email);\n```\n\n2. **SELECT Specific Columns**: Avoid SELECT *\n```sql\nSELECT name, email FROM users; -- Better\n```\n\n3. **Use JOINS Instead of Subqueries**: Generally more efficient\n\n4. **LIMIT Results**: When testing or pagination\n```sql\nSELECT * FROM orders LIMIT 100;\n```\n\n5. **Avoid Functions in WHERE**: They prevent index usage\n```sql\n-- Bad\nWHERE YEAR(date) = 2025\n-- Good\nWHERE date >= \'2025-01-01\'\n```\n\n6. **Use EXPLAIN**: Analyze query execution plan\n```sql\nEXPLAIN SELECT * FROM users WHERE email = \'test@test.com\';\n```',
      created_at: '2025-07-13T09:15:25Z'
    }
  ]
};

// Function to simulate API delay
export const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// Mock AI response generator
export const generateMockResponse = async (userMessage) => {
  await delay(1500); // Simulate API delay
  
  const responses = [
    "That's a great question! Let me help you with that.\n\nBased on current best practices, I'd recommend the following approach...",
    "I understand what you're looking for. Here's a comprehensive answer:\n\n1. First, consider the context\n2. Then, evaluate the options\n3. Finally, implement the solution",
    "Interesting! Here's what I think:\n\nThe key is to balance performance with maintainability. You should focus on writing clean, readable code first, then optimize as needed.",
    "Let me break this down for you:\n\n- **Point 1**: This is fundamental\n- **Point 2**: This builds on the first\n- **Point 3**: This completes the picture\n\nDoes this help clarify things?"
  ];
  
  return responses[Math.floor(Math.random() * responses.length)];
};