import React from 'react';
import ExtendableBar from './ExtendableBar';

const UsageExample = () => {
  return (
    <div>
      <ExtendableBar>
        <p>This is a simple text inside the ExtendableBar.</p>
      </ExtendableBar>
      <ExtendableBar>
        <form>
          <label htmlFor="name">Name:</label>
          <input type="text" id="name" name="name" />
          <button type="submit">Submit</button>
        </form>
      </ExtendableBar>
    </div>
  );
};

export default UsageExample;