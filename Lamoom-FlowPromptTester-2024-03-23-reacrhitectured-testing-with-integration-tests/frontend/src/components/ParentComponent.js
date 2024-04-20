import React from 'react';
import ExtendableBar from './ExtendableBar';

const ParentComponent = () => {
  return (
    <div>
      <ExtendableBar className="custom-class">
        <p>Content that may require more space</p>
        <p>Additional content that expands the bar</p>
      </ExtendableBar>
    </div>
  );
};

export default ParentComponent;