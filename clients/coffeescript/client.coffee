Sputnik = require("./sputnik").Sputnik

sputnik = new Sputnik "ws://127.0.0.1:8880/ws"
sputnik.connect()
got_cookie = false
sputnik.on "log", console.log
sputnik.on "warn", console.log
sputnik.on "error", console.error

sputnik.on "open", (session, details) ->
    console.log "Sputnik session open."
    #sputnik.follow "NETS2014"
    sputnik.authenticate "marketmaker", "marketmaker"
    #sputnik.getResetToken "marketmaker"

    #sputnik.token = 'MhjZ5mu5NMCzKnt4EqgIoQ=='
    #sputnik.username = 'marketmaker'
    #sputnik.changePasswordToken 'marketmaker'

sputnik.on "auth_success", ->
    console.log "Authenticated"
    if not got_cookie
        sputnik.getCookie()
    else
        sputnik.changePassword "marketmaker", "marketmaker"
        sputnik.changePassword "blah", "blah"
        sputnik.placeOrder("BTC/USD", 1, 400, 'SELL')
        sputnik.getAddress('BTC')

        sputnik.newAddress('BTC')
        sputnik.requestWithdrawal('USD', 3, 'my bank')
        sputnik.requestWithdrawal('BTC', 4, '2923')

        sputnik.openMarket('BTC/USD')

        sputnik.logout()


sputnik.on "auth_fail", ->
    console.log "Cannot login"

sputnik.on "cookie", (cookie) ->
    got_cookie = true
    sputnik.restoreSession "marketmaker", cookie
