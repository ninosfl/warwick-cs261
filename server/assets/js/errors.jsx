/* jshint esversion: 6 */

import React from 'react';
import { Alert, AlertTitle } from '@material-ui/lab';

export { ErrorMessage };

function ErrorMessage(props) {
    let err = JSON.parse(document.getElementById('error_message').textContent);
    return (
        <Alert severity="error">
            <AlertTitle>Error - Cannot find resource</AlertTitle>
            {err}
        </Alert>
    );
}