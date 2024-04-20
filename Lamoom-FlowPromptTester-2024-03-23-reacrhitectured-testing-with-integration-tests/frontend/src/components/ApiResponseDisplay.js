import React from 'react';
import PropTypes from 'prop-types';

const ApiResponseDisplay = ({ responseData, error }) => {
  console.log('ApiResponseDisplay rendering with:', { responseData, error });

  return (
    <div className="p-4">
      {error ? (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">Error:</strong>
          <span className="block sm:inline">{error}</span>
        </div>
      ) : (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative">
          <pre>{JSON.stringify(responseData, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

ApiResponseDisplay.propTypes = {
  responseData: PropTypes.oneOfType([PropTypes.object, PropTypes.array]),
  error: PropTypes.string,
};

ApiResponseDisplay.defaultProps = {
  responseData: null,
  error: null,
};

export default ApiResponseDisplay;