(function (av) {
    var k = av.CC_NUMBER = "number",
        ai = av.CC_EXP_MONTH = "exp_month",
        V = av.CC_EXP_YEAR = "exp_year",
        q = av.CC_HOLDER = "cardholder",
        au = av.CC_CVC = "cvc",
        R = av.CC_AMOUNT = "amount",
        ao = av.CC_AMOUNT_INT = "amount_int",
        am = av.CC_CURRENCY = "currency",
        g = av.DD_NUMBER = "number",
        j = av.DD_BANK = "bank",
        o = av.DD_HOLDER = "accountholder",
        i = av.DD_COUNTRY = "country",
        c = av.DD_BIC = "bic",
        z = av.DD_IBAN = "iban",
        an = av.E_CC_INVALID_NUMBER = "field_invalid_card_number",
        O = av.E_CC_INVALID_EXPIRY = "field_invalid_card_exp",
        Z = av.E_CC_INVALID_EXP_MONTH = "field_invalid_card_exp_month",
        at = av.E_CC_INVALID_EXP_YEAR = "field_invalid_card_exp_year",
        B = av.E_CC_INVALID_CVC = "field_invalid_card_cvc",
        aw = av.E_CC_INVALID_HOLDER = "field_invalid_card_holder",
        u = av.E_CC_INVALID_AMOUNT = "field_invalid_amount",
        r = av.E_CC_INVALID_AMOUNT_INT = "field_invalid_amount_int",
        l = av.E_CC_INVALID_CURRENCY = "field_invalid_currency",
        F = av.E_DD_INVALID_NUMBER = "field_invalid_account_number",
        C = av.E_DD_INVALID_BANK = "field_invalid_bank_code",
        M = av.E_DD_INVALID_HOLDER = "field_invalid_account_holder",
        s = av.E_DD_INVALID_BANK_DATA = "field_invalid_bank_data",
        X = av.E_DD_INVALID_IBAN = "field_invalid_iban",
        m = av.E_DD_INVALID_COUNTRY = "field_invalid_country",
        ae = av.E_DD_INVALID_BIC = "field_invalid_bic",
        A = av.DEBIT_TYPE_ELV = "elv",
        ak = av.DEBIT_TYPE_SEPA = "sepa";
    var N = {};
    av.config = function N(ay, az) {
        if (az !== undefined) {
            N[ay] = az
        }
        return N[ay]
    };
    var aa = av.increaseMonetaryUnit = function aa(aA, az, ay) {
        az = az ? az : 100;
        ay = ay ? ay : 2;
        aA = (aA / az).toFixed(ay);
        return aA
    };
    if (!Array.prototype.indexOf) {
        Array.prototype.indexOf = function (aA) {
            if (this == null) {
                throw new TypeError()
            }
            var aB = Object(this);
            var ay = aB.length >>> 0;
            if (ay === 0) {
                return -1
            }
            var aC = 0;
            if (arguments.length > 1) {
                aC = Number(arguments[1]);
                if (aC != aC) {
                    aC = 0
                } else {
                    if (aC != 0 && aC != Infinity && aC != -Infinity) {
                        aC = (aC > 0 || -1) * Math.floor(Math.abs(aC))
                    }
                }
            }
            if (aC >= ay) {
                return -1
            }
            var az = aC >= 0 ? aC : Math.max(ay - Math.abs(aC), 0);
            for (; az < ay; az++) {
                if (az in aB && aB[az] === aA) {
                    return az
                }
            }
            return -1
        }
    }
    var W = {
        "4012888888881881": true,
        "5169147129584558": true
    };
    var E = [{
        type: "American Express",
        pattern: /^3[47]/,
        luhn: true,
        cvcLength: [3, 4],
        numLength: [15]
    }, {
        type: "Discover",
        pattern: /^(6011|622(1[2-90][6-9]|[2-8]\d{2}|9[0-1]\d|92[0-5])|64[4-9]|65)/,
        luhn: true,
        cvcLength: [3],
        numLength: [16]
    }, {
        type: "UnionPay",
        pattern: /^62/,
        luhn: false,
        cvcLength: [3],
        numLength: [16, 17, 18, 19]
    }, {
        type: "Diners Club",
        pattern: /^(30[0-5]|36|38)/,
        luhn: true,
        cvcLength: [3],
        numLength: [14]
    }, {
        type: "JCB",
        pattern: /^35([3-8][0-9]|2[8-9])/,
        luhn: true,
        cvcLength: [3],
        numLength: [16]
    }, {
        type: "Maestro",
        pattern: /^(5018|5020|5038|5893|6304|6331|6703|6759|676[1-3]|6799|0604)/,
        luhn: true,
        cvcLength: [0, 3, 4],
        numLength: [12, 13, 14, 15, 16, 17, 18, 19]
    }, {
        type: "MasterCard",
        pattern: /^(5[1-5])/,
        luhn: true,
        cvcLength: [3],
        numLength: [16]
    }, {
        type: "Visa",
        pattern: /^4/,
        luhn: true,
        cvcLength: [3],
        numLength: [13, 16]
    }];
    var J = av.tr = function J(ay) {
        return ((ay || "") + "").replace(/^\s+|\s+$/g, "")
    };
    var ac = av.clr = function ac(ay) {
        return (ay + "").replace(/\s+|-/g, "")
    };
    var S = av.flip = function S(ay) {
        return (ay + "").split("").reverse().join("")
    };
    var D = av.chksum = function D(aD) {
        if (aD.match(/^\d+$/) === null) {
            return false
        }
        var aC = S(aD);
        var aA = aC.length;
        var ay;
        var az = 0;
        var aB;
        for (ay = 0; ay < aA; ++ay) {
            aB = parseInt(aC.charAt(ay), 10);
            if (0 !== ay % 2) {
                aB *= 2
            }
            az += (aB < 10) ? aB : aB - 9
        }
        return (0 !== az && 0 === az % 10)
    };
    var w = av.toFormEncoding = function w(aB, aA) {
        var aC = [];
        for (var aD in aB) {
            if (aB.hasOwnProperty(aD)) {
                var ay = aA ? aA + "[" + aD + "]" : aD;
                var az = aB[aD];
                aC.push("object" === typeof az ? w(az, ay) : encodeURIComponent(ay) + "=" + encodeURIComponent(az))
            }
        }
        return aC.join("&")
    };

    function b(aB) {
        aB = ac(aB);
        var az, aA, ay;
        for (aA = 0, ay = E.length; aA < ay; aA++) {
            az = E[aA];
            if (az.pattern.test(aB)) {
                return az
            }
        }
    }
    var ab = av.validateCardNumber = function ab(az) {
        az = ac(az);
        var ay = b(az);
        if (!az || !ay) {
            return false
        }
        if (ay.luhn && false == D(az)) {
            return false
        }
        return ay.numLength.indexOf(az.length) != -1
    };
    var af = av.validateCvc = function af(aB, aC) {
        aB = J(aB);
        if (!aC) {
            return null !== aB.match(/^\d{3,4}$/)
        }
        aC = ac(aC);
        var az, aA, ay;
        for (aA = 0, ay = E.length; aA < ay; aA++) {
            az = E[aA];
            if (az.pattern.test(aC)) {
                if (aB.length > 0) {
                    return az.cvcLength.indexOf(aB.length) != -1 && null !== aB.match(/^\d+$/)
                } else {
                    return az.cvcLength.indexOf(aB.length) != -1
                }
            }
        }
        return false
    };
    var ar = av.validateExpMonth = function ar(ay) {
        return /^([1-9]|0[1-9]|1[012])$/.test(J(ay))
    };
    var p = av.validateExpYear = function p(ay) {
        return /^\d{4}$/.test(J(ay))
    };
    var T = av.validateExpiry = function T(aC, aA) {
        if (!ar(aC) || !p(aA)) {
            return false
        }
        aC = parseInt(J(aC), 10);
        aA = parseInt(J(aA), 10);
        var aB = new Date(),
            ay = aB.getFullYear(),
            az = aB.getMonth() + 1;
        return aA > ay || (aA === ay && aC >= az)
    };
    var y = av.validateAmount = function y(ay) {
        ay = J(ay);
        return /^([0-9]+)(\.[0-9]+)?$/.test(ay)
    };
    var d = av.validateAmountInt = function d(ay) {
        ay = J(ay);
        return /^[0-9]+$/.test(ay)
    };
    var t = av.validateCurrency = function t(ay) {
        ay = J(ay);
        return /^[A-Z]{3}$/.test(ay)
    };
    var a = av.validateHolder = function a(ay) {
        if (!ay) {
            return false
        }
        return /^.{4,128}$/.test(J(ay))
    };
    var al = av.validateAccountNumber = function al(ay) {
        return /^\d+$/.test(ac(ay))
    };
    var h = av.validateBankCode = function h(ay) {
        return /^\d{8}$/.test(ac(ay))
    };
    var K = av.cardType = function K(aA) {
        var az;
        if (ab(aA)) {
            az = b(aA), ay
        }
        var ay = az ? az.type : "Unknown";
        return ay
    };
    var f = av.getApiKey = function f() {
        if (typeof PAYMILL_PUBLIC_KEY != "undefined") {
        	return PAYMILL_PUBLIC_KEY 
        }

        if (typeof this.paymill.PAYMILL_PUBLIC_KEY != "undefined") {
        	return this.paymill.PAYMILL_PUBLIC_KEY 
        }

        throw new Error("No public api key is set. You need to set the global PAYMILL_PUBLIC_KEY variable to your public api key in order to use this api.")
    };
    var L = av.isTestKey = function L(ay) {
        return (ay + "").match(/^\d{10}/) || (typeof PAYMILL_TEST_MODE !== "undefined" && PAYMILL_TEST_MODE === true)
    };
    av.transport = {
        execute: function n(az, ay, aA) {
            throw new Error("paymill.transport.execute() not implemented. Wtf?")
        }
    };
    var ah = av.createToken = function ah(aC, aE, ay, aB) {
        var aD = f(),
            aA = {
                type: "createToken"
            };
        try {
            aA.data = (aC[j] === undefined && aC[c] === undefined) ? x(aC, aD) : v(aC);
            av.transport.execute(aD, aA, aE, ay, aB)
        } catch (az) {
            setTimeout(function () {
                aE({
                    apierror: az
                })
            }, 0)
        }
    };

    function ax(aA, ay) {
        var az = new XMLHttpRequest();
        if ("withCredentials" in az) {
            az.open(aA, ay, true)
        } else {
            if (typeof XDomainRequest != "undefined") {
                az = new XDomainRequest();
                az.open(aA, ay)
            } else {
                az = null
            }
        }
        return az
    }
    var U = av.getBankName = function U(aC, aD) {
        if (aC == "") {
            return
        }
        var aB = "";
        try {
            aB = ag(aC)
        } catch (ay) {
            aD({
                apierror: ay
            });
            return
        }
        if (typeof JSON !== "object") {
            setTimeout(function () {
                aD({
                    apierror: "Woops, there was an error creating the request."
                })
            }, 0);
            return
        }
        var az = av.getBlzUrl(aB);
        var aA = ax("GET", az);
        if (!aA) {
            setTimeout(function () {
                aD({
                    apierror: "Woops, there was an error creating the request."
                })
            }, 0);
            return
        }
        aA.onload = function () {
            var aF = aA.responseText;
            var aE = JSON.parse(aF).data;
            if (typeof aE.success !== "undefined") {
                if (aE.success) {
                    aD(null, aE.name)
                } else {
                    aD({
                        apierror: aE.error
                    })
                }
            } else {
                aD({
                    apierror: "Woops, there was an error extracting the request."
                })
            }
        };
        aA.onerror = function () {
            aD({
                apierror: "Woops, there was an error making the request."
            })
        };
        aA.send()
    };

    function ag(az) {
        if (/\D/.test(az)) {
            var ay = az.toString();
            if (ay.length == 8) {
                return ay + "XXX"
            } else {
                if (ay.length == 11) {
                    return ay
                } else {
                    if (ad(ay)) {
                        return ay.substr(4, 8)
                    } else {
                        throw X
                    }
                }
            }
        } else {
            if (az.toString().length != 8) {
                throw C
            }
            return az.toString()
        }
    }
    var e = av.getBlzUrl = function e(ay) {
        return "https://bridge.paymill.de/blz/" + ay
    };

    function H(az, ay) {
        return (av.isTestKey(az) && W[ay] !== true)
    }

    function x(aA, az) {
        var ay = {};
        ay[k] = ac(aA[k]);
        ay[ai] = J(aA[ai]);
        ay[V] = J(aA[V]);
        ay[au] = J(aA[au]);
        ay[q] = J(aA[q]);
        ay[R] = J(aA[R]);
        ay[ao] = J(aA[ao]);
        ay[am] = J(aA[am]);
        ay[ai] = ("0" + ay[ai]).slice(-2);
        if (!ab(ay[k])) {
            throw an
        }
        if (!T(ay[ai], ay[V])) {
            throw O
        }
        if (!af(ay[au], ay[k])) {
            throw B
        }
        if (ay[q] === undefined) {
            delete ay[q]
        }
        var aB = H(az, ay[k]);
        if (d(ay[ao])) {
            ay[R] = aa(ay[ao]);
            delete ay[ao]
        } else {
            if (ay[ao] !== undefined && ay[ao] !== "") {
                throw r
            }
        } if (y(ay[R])) {
            ay[R] = aa(ay[R], 1, 2)
        } else {
            if (ay[R] !== undefined && ay[R] !== "") {
                throw u
            }
        } if (ay[am] !== undefined && ay[am] !== "" && !t(ay[am])) {
            throw l
        }
        if ((ay[R] === undefined || ay[R] === "") && (ay[am] !== undefined && ay[am] !== "")) {
            throw u
        } else {
            if ((ay[R] !== undefined && ay[R] !== "") && (ay[am] === undefined || ay[am] === "")) {
                throw l
            }
        }
        return ay
    }

    function v(aA) {
        var az = {};
        var ay = P(aA);
        if (ay == ak) {
            az[z] = ac(aA[z]);
            az[c] = ac(aA[c]);
            if (!ad(az[z], true)) {
                throw X
            }
            if (!ap(az[c])) {
                throw ae
            }
            az[i] = aA[z].substr(0, 2)
        } else {
            if (ay == A) {
                az[g] = ac(aA[g]);
                az[j] = ac(aA[j]);
                if (!al(az[g])) {
                    throw F
                }
                if (!h(az[j])) {
                    throw C
                }
                az[i] = "DE"
            } else {
                throw s
            }
        }
        az[o] = J(aA[o]);
        if (az[o] === undefined || az[o] === "") {
            throw M
        }
        if (!a(az[o])) {
            throw M
        }
        return az
    }

    function P(az) {
        var ay = "unknown";
        if ((az[z] !== undefined) && (az[c] !== undefined)) {
            ay = ak
        } else {
            if ((az[j] !== undefined) && (az[g] !== undefined)) {
                ay = A
            }
        }
        return ay
    }
    var ad = av.validateIban = function ad(az, ay) {
        try {
            return aj(az)
        } catch (aA) {
            if (ay) {
                throw aA
            } else {
                return false
            }
        }
    };

    function aj(ay) {
        ay = ac(ay.toString());
        if (ay.length < 5) {
            throw X
        }
        if (!/^[a-z]{2}[0-9]{2}[a-z0-9]+$/i.test(ay)) {
            throw X
        }
        var aA = ay.substr(0, 2);
        if (Y[aA] === undefined) {
            throw m
        }
        var az = Y[aA];
        if (az != ay.length) {
            throw X
        }
        if (!aq(ay)) {
            throw X
        }
        return true
    }
    var Y = {
        DE: 22
    };
    var G = {
        A: "10",
        B: "11",
        C: "12",
        D: "13",
        E: "14",
        F: "15",
        G: "16",
        H: "17",
        I: "18",
        J: "19",
        K: "20",
        L: "21",
        M: "22",
        N: "23",
        O: "24",
        P: "25",
        Q: "26",
        R: "27",
        S: "28",
        T: "29",
        U: "30",
        V: "31",
        W: "32",
        X: "33",
        Y: "34",
        Z: "35"
    };

    function aq(az) {
        var ay = I(az);
        return Q(ay) === "01"
    }

    function I(ay) {
        var aA = ay.substr(4) + ay.substr(0, 4);
        aA = aA.toUpperCase();
        for (var az in G) {
            aA = aA.replace(az, G[az])
        }
        return aA
    }

    function Q(az) {
        var aD = 0;
        var aB = 9;
        var ay = true;
        var aC = "";
        while (ay) {
            if (az.substr(aD, aB).length < 7) {
                ay = false;
                aB = az.substr(aD, aB).length
            }
            var aA = aC + az.substr(aD, aB);
            aC = (aA % 97) + "";
            if (aC.length === 1) {
                aC = "0" + aC
            }
            aD = aD + aB;
            aB = 7
        }
        return aC
    }
    var ap = av.validateBic = function ap(ay) {
        ay = ac(ay);
        return /[A-Z]{4}(DE)[A-Z1-9]{2}([A-Z\d]{3})?/.test(ay)
    }
})(window.paymill = {});
(function (b, d, a) {
    if (b === undefined || b == null) {
        throw new Error("paymill object not initialized")
    }
    b.getDeviceIdent = function c() {
        di = {
            v: "paymill-com"
        };
        (function () {
            var f = a.createElement("script");
            f.type = "text/javascript";
            f.async = true;
            f.src = "https://showcase.deviceident.com/pmcom/di-js.js";
            var e = a.getElementsByTagName("script")[0];
            e.parentNode.insertBefore(f, e)
        })()
    }
})(window.paymill, window, document);
(function (a) {
    a.dom = {
        css: function (c, b) {
            for (var d in b) {
                val = b[d];
                if (typeof val === "number") {
                    val += "px"
                }
                c.style[d] = val
            }
        },
        computedStyle: function (c, d) {
            var b = "";
            if (document.defaultView && document.defaultView.getComputedStyle) {
                b = document.defaultView.getComputedStyle(c, "").getPropertyValue(d)
            } else {
                if (c.currentStyle) {
                    d = d.replace(/\-(\w)/g, function (e, f) {
                        return f.toUpperCase()
                    });
                    b = c.currentStyle[d]
                }
            }
            return b
        },
        bind: function (c, b, d) {
            if (c.addEventListener) {
                c.addEventListener(b, d, false)
            } else {
                if (c.attachEvent) {
                    c.attachEvent("on" + b, d)
                }
            }
        },
        innerWidth: function () {
            if (typeof window.innerWidth === "number") {
                return window.innerWidth
            }
            if (window.documentElement && typeof window.documentElement.clientWidth === "number") {
                return window.documentElement.clientWidth
            }
            if (document.body && typeof document.body.clientWidth === "number") {
                return document.body.clientWidth
            }
        },
        innerHeight: function () {
            if (typeof window.innerHeight === "number") {
                return window.innerHeight
            }
            if (window.documentElement && typeof window.documentElement.clientHeight === "number") {
                return window.documentElement.clientHeight
            }
            if (document.body && typeof document.body.clientHeight === "number") {
                return document.body.clientHeight
            }
        }
    }
})(window.paymill === undefined ? window.paymill = {} : window.paymill);
(function (a, k, o) {
    if (a === undefined || a == null) {
        throw new Error("paymill object not initialized")
    }
    var f = o.head || o.getElementsByTagName("head")[0] || o.documentElement;
    var b = {
        test: "https://test-token.paymill.de",
        live: "https://token-v2.paymill.de"
    };
    var q = {
        test: "https://test-token.paymill.de",
        live: "https://token.paymill.de"
    };
    var j = {
        test: "https://test-tds.paymill.de/end.php",
        live: "https://tds.paymill.de/end.php"
    };
    var c = "ACK",
        t = "NOK",
        p = "CONNECTOR_TEST",
        v = "LIVE";
    var e = {
        "100.100.600": a.E_CC_INVALID_CVC,
        "100.100.601": a.E_CC_INVALID_CVC,
        "100.100.303": a.E_CC_INVALID_EXPIRY,
        "100.100.304": a.E_CC_INVALID_EXPIRY,
        "100.100.301": a.E_CC_INVALID_EXP_YEAR,
        "100.100.300": a.E_CC_INVALID_EXP_YEAR,
        "100.100.201": a.E_CC_INVALID_EXP_MONTH,
        "100.100.200": a.E_CC_INVALID_EXP_MONTH,
        "100.100.100": [a.E_CC_INVALID_NUMBER, a.E_DD_INVALID_NUMBER],
        "100.100.101": [a.E_CC_INVALID_NUMBER, a.E_DD_INVALID_NUMBER],
        "100.100.400": [a.E_CC_INVALID_HOLDER, a.E_DD_INVALID_HOLDER],
        "100.100.401": [a.E_CC_INVALID_HOLDER, a.E_DD_INVALID_HOLDER],
        "100.100.402": [a.E_CC_INVALID_HOLDER, a.E_DD_INVALID_HOLDER],
        "600.200.500": "invalid_payment_data"
    };
    var h = {};
    a.transport.buildRequestUrl = function (A, z, y) {
        var w, x = a.toFormEncoding(z);
        if (y.bic !== undefined || y.iban !== undefined || y.bank !== undefined) {
            w = a.isTestKey(A) ? q.test : q.live
        } else {
            w = a.isTestKey(A) ? b.test : b.live
        } if (w.indexOf("?") >= 0) {
            w += "&" + x
        } else {
            w += "?" + x
        }
        return w
    };

    function s(A, F, E, x) {
        var D = null,
            z = null,
            y = null;
        if (A === null) {
            return F(u("internal_server_error"), null)
        } else {
            if (A.error) {
                if (/check channelId or login/.test(A.error.message)) {
                    return F(u("invalid_public_key"))
                }
                return F(u("unknown_error", A.error.message || A.error))
            } else {
                var w = A.transaction.processing;
                if (w.result === c) {
                    var y = A.transaction.identification.uniqueId,
                        C = A.transaction.customer,
                        B = A.transaction.account;
                    if (C) {
                        z = {
                            token: y,
                            bin: B.bin,
                            binCountry: C.address.country,
                            brand: B.brand,
                            last4Digits: B.last4Digits,
                            ip: C.contact.ip,
                            ipCountry: C.contact.ipCountry
                        }
                    } else {
                        z = {
                            token: y
                        }
                    } if (w.redirect) {
                        g(A, y, F, E, x)
                    } else {
                        return F(null, z)
                    }
                } else {
                    return F(m(A), null)
                }
            }
        }
    }
    var n = [];

    function r(F, A) {
        var x = F.url,
            P = F.params;
        var D = o.body || o.getElementsByTagName("body")[0];
        var I = 600,
            H = 400,
            z = -60;
        var O = parseInt(a.dom.computedStyle(D, "margin-left"), 10) + parseInt(a.dom.computedStyle(D, "padding-left"), 10),
            N = parseInt(a.dom.computedStyle(D, "margin-top"), 10) + parseInt(a.dom.computedStyle(D, "padding-top"), 10);
        var J = a.dom.innerWidth(),
            M = a.dom.innerHeight();
        var y = o.createElement("div");
        y.style.cssText = "position:fixed;z-index:2147483646;top:-" + N + "px;left:-" + O + "px;width:" + (k.innerWidth + O) + "px;height:" + (k.innerHeight + N) + "px;background-color:#000;opacity:0.5;";
        var L = o.createElement("div");
        L.style.cssText = "position:fixed; z-index: 2147483647; width: " + I + "px; height: " + H + "; border-radius: 5px; background: white; font-family: sans-serif; font-size: 14px; -webkit-box-shadow: 0 0 50px rgba(0,0,0,0.3); -moz-box-shadow:  0 0 50px rgba(0,0,0,0.3); box-shadow: 0 0 50px rgba(0,0,0,0.3);";
        L.style.left = Math.floor(Math.max(0, J / 2 - I / 2)) + "px";
        L.style.top = Math.floor(Math.max(0, M / 2 - H / 2) + z) + "px";
        L.innerHTML = "<div style=\"border-bottom: 1px solid #c0c0c0!important; -webkit-border-top-right-radius: 5px; -moz-border-radius-topright: 5px; border-top-right-radius: 5px; -webkit-border-bottom-right-radius: 0; -moz-border-radius-bottomright: 0; border-bottom-right-radius: 0; -webkit-border-bottom-left-radius: 0; -moz-border-radius-bottomleft: 0; border-bottom-left-radius: 0; -webkit-border-top-left-radius: 5px; -moz-border-radius-topleft: 5px; border-top-left-radius: 5px; background-color: #dcdcdc; background-image: -moz-linear-gradient(top, #ededed, #c3c3c3); background-image: -ms-linear-gradient(top, #ededed, #c3c3c3); background-image: -webkit-gradient(linear, 0 0, 0 100%, from(#ededed), to(#c3c3c3)); background-image: -webkit-linear-gradient(top, #ededed, #c3c3c3); background-image: -o-linear-gradient(top, #ededed, #c3c3c3); background-image: linear-gradient(top, #ededed, #c3c3c3); background-repeat: repeat-x; filter: progid:DXImageTransform.Microsoft.gradient(startColorstr='#ededed', endColorstr='#c3c3c3', GradientType=0); *zoom: 1; padding: 10px 0 0 0; height: 26px; text-align: center;\">3D-Secure</div><iframe style=\"border:none;width:" + I + "px;height:" + H + 'px;"><html><body></body></html></iframe><div style="padding: 14px 15px 15px; margin-bottom: 0; text-align: right; background-color: #f5f5f5; border-top: 1px solid #ddd; -webkit-border-radius: 0 0 6px 6px; -moz-border-radius: 0 0 6px 6px; border-radius: 0 0 6px 6px; -webkit-box-shadow: inset 0 1px 0 #ffffff; -moz-box-shadow: inset 0 1px 0 #ffffff; box-shadow: inset 0 1px 0 #ffffff; *zoom: 1;"><input type="submit" value="' + (a.config("3ds_cancel_label") || "Cancel") + "\" style=\"display: inline-block; *display: inline; *zoom: 1; padding: 4px 10px 4px; margin-bottom: 0; font-size: 13px; line-height: 20px; *line-height: 20px; color: #333333; text-align: center; text-shadow: 0 1px 1px rgba(255, 255, 255, 0.75); vertical-align: middle; cursor: pointer; background-color: #f5f5f5; background-image: -moz-linear-gradient(top, #ffffff, #e6e6e6); background-image: -ms-linear-gradient(top, #ffffff, #e6e6e6); background-image: -webkit-gradient(linear, 0 0, 0 100%, from(#ffffff), to(#e6e6e6)); background-image: -webkit-linear-gradient(top, #ffffff, #e6e6e6); background-image: -o-linear-gradient(top, #ffffff, #e6e6e6); background-image: linear-gradient(top, #ffffff, #e6e6e6); background-repeat: repeat-x; filter: progid:DXImageTransform.Microsoft.gradient(startColorstr='#ffffff', endColorstr='#e6e6e6', GradientType=0); border-color: #e6e6e6 #e6e6e6 #bfbfbf; border-color: rgba(0, 0, 0, 0.1) rgba(0, 0, 0, 0.1) rgba(0, 0, 0, 0.25); *background-color: #e6e6e6; filter: progid:DXImageTransform.Microsoft.gradient(enabled = false); border: 1px solid #cccccc; *border: 0; border-bottom-color: #b3b3b3; -webkit-border-radius: 4px; -moz-border-radius: 4px; border-radius: 4px; *margin-left: .3em; -webkit-box-shadow: inset 0 1px 0 rgba(255,255,255,.2), 0 1px 2px rgba(0,0,0,.05); -moz-box-shadow: inset 0 1px 0 rgba(255,255,255,.2), 0 1px 2px rgba(0,0,0,.05); box-shadow: inset 0 1px 0 rgba(255,255,255,.2), 0 1px 2px rgba(0,0,0,.05);\"></div>";
        var B = L.firstChild.nextSibling.nextSibling.firstChild;
        var C = L.firstChild.nextSibling;
        a.dom.bind(B, "click", A);
        D.insertBefore(y, D.firstChild);
        D.insertBefore(L, D.firstChild);
        n.push(y);
        n.push(L);
        var G = C.contentWindow || C.contentDocument;
        if (G.document) {
            G = G.document
        }
        var w = G.createElement("form");
        w.method = "post";
        w.action = x;
        for (var K in P) {
            var E = G.createElement("input");
            E.type = "hidden";
            E.name = K;
            E.value = decodeURIComponent(P[K]);
            w.appendChild(E)
        }
        if (G.body) {
            G.body.appendChild(w)
        } else {
            G.appendChild(w)
        }
        w.submit()
    }

    function d() {
        var w = n.length;
        while (w--) {
            if (n[w] && n[w].parentNode) {
                n[w].parentNode.removeChild(n[w])
            }
        }
        n.length = 0
    }

    function g(B, x, H, E, w) {
        var D = B.transaction.processing.redirect;
        var F = B.transaction.mode === p;
        var A = {
            url: decodeURIComponent(D.url),
            params: {}
        };
        for (var z in D.parameters) {
            A.params[z] = D.parameters[z]
        }
        var G = E || r,
            y = w || d,
            C = j[F ? "test" : "live"];
        G(A, function () {
            y();
            H(u("3ds_cancelled"))
        });
        a.receiveMessage();
        a.receiveMessage(function (J, I) {
            if (J.data === "ok") {
                y();
                H(null, {
                    token: x
                })
            }
            if (J.data === "cancelled") {
                y();
                H(u("3ds_cancelled"))
            }
        }, C.replace(/([^:]+:\/\/[^\/]+).*/, "$1"))
    }

    function m(y) {
        var x = y.transaction.processing["return"].code,
            w = y.transaction.processing["return"].message;
        if (e[x] !== undefined) {
            var z = e[x];
            if (Object.prototype.toString.apply(z) === "[object Array]") {
                return u(z[0])
            }
            return u(z)
        }
        return u("unknown_error", w)
    }

    function u(x, w) {
        if (w === undefined) {
            return {
                apierror: x
            }
        }
        return {
            apierror: x,
            message: w
        }
    }
    var l = {
        exp_month: "account.expiry.month",
        exp_year: "account.expiry.year",
        cardholder: "account.holder",
        number: "account.number",
        amount: "presentation.amount3D",
        currency: "presentation.currency3D",
        cvc: "account.verification",
        accountholder: "account.holder",
        bank: "account.bank",
        country: "account.country",
        iban: "account.iban",
        bic: "account.bic"
    };
    a.transport.execute = function i(B, A, G, F, x) {
        var D = "paymillCallback" + parseInt(Math.random() * 4294967295, 10);
        h[D] = null;
        a.transport[D] = function (I) {
            h[D] = I
        };
        var w = a.isTestKey(B),
            E = w ? p : v,
            H = j[w ? "test" : "live"];
        H += "?parentUrl=" + encodeURIComponent(encodeURIComponent(k.location.href)) + "&";
        var z = {
            "transaction.mode": E,
            "channel.id": B,
            "response.url": H,
            jsonPFunction: "window.paymill.transport." + D
        };
        for (var y in A.data) {
            if (l[y] === undefined) {
                continue
            }
            z[l[y]] = A.data[y]
        }
        var C = o.createElement("script");
        C.async = "async";
        C.src = a.transport.buildRequestUrl(B, z, A.data);
        C.onload = C.onerror = C.onreadystatechange = function (J) {
            if (!C.readyState || /loaded|complete/.test(C.readyState)) {
                var I = h[D];
                delete paymill.transport[D];
                delete h[D];
                C.onload = C.onerror = C.onreadystatechange = null;
                f.removeChild(C);
                s(I, G, F, x)
            }
        };
        f.insertBefore(C, f.firstChild)
    }
})(window.paymill, window, document);
(function (c) {
    var e, f, d = 1,
        b;
    c.postMessage = function a(h, j, i) {
        if (!j) {
            return
        }
        i = i || parent;
        if (window.postMessage) {
            i.postMessage(h, j.replace(/([^:]+:\/\/[^\/]+).*/, "$1"))
        } else {
            if (j) {
                i.location = j.replace(/#.*$/, "") + "#" + (+new Date) + (d++) + "&" + h
            }
        }
    };
    c.receiveMessage = function g(i, h) {
        if (window.postMessage) {
            if (i) {
                b = function (j) {
                    if ((typeof h === "string" && j.origin !== h) || (Object.prototype.toString.call(h) === "[object Function]" && h(j.origin) === !1)) {
                        return !1
                    }
                    i(j)
                }
            }
            if (window.addEventListener) {
                window[i ? "addEventListener" : "removeEventListener"]("message", b, !1)
            } else {
                if (b) {
                    window[i ? "attachEvent" : "detachEvent"]("onmessage", b)
                }
            }
        } else {
            e && clearInterval(e);
            e = null;
            if (i) {
                e = setInterval(function () {
                    var k = document.location.hash,
                        j = /^#?\d+&/;
                    if (k !== f && j.test(k)) {
                        f = k;
                        i({
                            data: k.replace(j, "")
                        })
                    }
                }, 100)
            }
        }
    }
})(window.paymill === undefined ? window.paymill = {} : window.paymill);
