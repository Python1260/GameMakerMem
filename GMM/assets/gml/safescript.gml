/* ERROR-SAFE SCRIPT */

try {
    $CODE$
}
catch (error) {
    var d = [error.message, error.longMessage, error.script, error.line, error.stacktrace];
    show_message("An error occurred while executing GML: " + error.message);
}