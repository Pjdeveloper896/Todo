// pages/index.tsx
import { useState } from 'react';
import { Todo } from './Todo';

export default function Home() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [newTodo, setNewTodo] = useState<string>('');

  // Handle adding a new to-do
  const addTodo = () => {
    if (newTodo.trim() !== '') {
      const newTodoItem: Todo = {
        id: Date.now(),  // Unique ID based on timestamp
        text: newTodo,
      };
      setTodos([...todos, newTodoItem]);
      setNewTodo('');
    }
  };

  // Handle removing a to-do
  const removeTodo = (id: number) => {
    setTodos(todos.filter(todo => todo.id !== id));
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>To-Do List</h1>

      {/* Input for adding new todo */}
      <input
        type="text"
        value={newTodo}
        onChange={(e) => setNewTodo(e.target.value)}
        placeholder="Add a new task"
        style={{ marginRight: '10px' }}
      />
      <button onClick={addTodo}>Add</button>

      <ul style={{ marginTop: '20px' }}>
        {todos.map((todo) => (
          <li key={todo.id} style={{ marginBottom: '10px' }}>
            {todo.text}
            <button
              onClick={() => removeTodo(todo.id)}
              style={{ marginLeft: '10px', color: 'red' }}
            >
              Remove
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
