'use client';

import React from 'react';
import TaskList from '../../components/Task/TaskList';

// Client wrapper component to avoid passing event handlers from server to client components
const ClientTaskListWrapper = () => {
  return <TaskList />;
};

export default ClientTaskListWrapper;