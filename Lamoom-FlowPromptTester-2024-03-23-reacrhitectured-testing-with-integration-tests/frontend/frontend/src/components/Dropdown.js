import React from 'react';

const Dropdown = ({ label, options, value, onChange }) => {
  return (
    <div className="dropdown">
      <label htmlFor="dropdown">{label}</label>
      <select id="dropdown" value={value} onChange={onChange}>
        {options.map((option, index) => (
          <option key={index} value={option}>
            {option}
          </option>
        ))}
      </select>
    </div>
  );
};

export default Dropdown;