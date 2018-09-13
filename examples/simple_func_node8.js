function handler(event) {
    console.log('NodeJS version: ' + process.version);
    return 'Hello friend, you are passing ' + event.length + ' arguments';
}
