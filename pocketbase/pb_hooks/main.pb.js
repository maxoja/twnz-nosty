// pb_hooks/main.pb.js

routerAdd("GET", "/hello/:name", (c) => {
    let name = c.pathParam("name")
    return c.json(200, { "message": "Hello " + name })
})

routerAdd('GET', '/checkDevice/:userId/:deviceId', (c) => {
    const COL_DEVICES = 'devices'
    const USER_ID = 'userId'
    const DEVICE_ID = 'deviceId'

    const userId = c.pathParam(USER_ID)
    const deviceId = c.pathParam(DEVICE_ID)
    console.log('userId', userId)
    console.log('deviceId', deviceId)
    const deviceRecords = $app.dao().findRecordsByFilter(
        COL_DEVICES,
        `userId={:userId}`,
        "-created", // sorting
        1, // limit
        0, // offset
        {userId}
    )

    if (deviceRecords.length === 0) {
        return c.json(200, {"registered": false, "authorized": false})
    }

    if (deviceRecords.length === 1 && deviceRecords[0].getString(DEVICE_ID) === deviceId) {
        return c.json(200, {"registered": true, "authorized": true})
    }

    return c.json(200, {"registered": true, "authorized": false})
})

routerAdd('GET', '/registerDevice/:userId/:deviceId', (c) => {
    const COL_DEVICES = 'devices'
    const USER_ID = 'userId'
    const DEVICE_ID = 'deviceId'

    const userId = c.pathParam(USER_ID)
    const deviceId = c.pathParam(DEVICE_ID)
    const deviceRecords = $app.dao().findRecordsByFilter(
        COL_DEVICES,
        `userId = {:userId}`,
        "-created", // sorting
        1, // limit
        0, // offset
        {'userId': userId}
    )

    if (deviceRecords.length === 1) {
        return c.json(200, {"alreadyRegistered": true, "success": false})
    }

    const collection = $app.dao().findCollectionByNameOrId("devices")
    const record = new Record(collection)

    const form = new RecordUpsertForm($app, record)
    form.loadData({
        [USER_ID]: userId,
        [DEVICE_ID]: deviceId
    })
    form.submit()
    return c.json(200, {"alreadyRegistered": false, "success": true})
})


// routerAdd('PATCH', '/posts/:postId', (c) => {
//   const postId = c.pathParam('postId')
//
//   // Get body data
//   const body = $apis.requestInfo(c).data
//   const status = body.status
//
//   // Find a record by ID on the "posts" collection
//   const record = $app.dao().findRecordById('posts', postId)
//
//   // If the record doesn't exist, return a 404
//   // Perhaps you can return a 40X if the user doesn't have permission to update the record etc
//   if (!record) {
//     return c.json(404, {
//       error: 'Record not found',
//     })
//   }
//
//   // Update the record with the new status
//   record.set('status', status)
//
//   // Save the record
//   $app.dao().saveRecord(record)
//
//   // Expand record before we return it
//   $app.dao().expandRecord(record, ['user', 'comments'], null)
//
//   // Return the record
//   return c.json(200, {
//     record,
//   })
// })