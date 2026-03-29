/**
 * class Qrcode
 * @param typeNumber 1 to 40
 * @param errorCorrectionLevel 'L','M','Q','H'
 */
class QrCode {
    constructor(typeNumber, errorCorrectionLevel) {
        this._typeNumber = typeNumber;
        this._errorCorrectionLevel = QRErrorCorrectionLevel[errorCorrectionLevel];
        this._modules = null;
        this._moduleCount = 0;
        this._dataCache = null;
        this._dataList = [];
    }

    addData(data, mode) {
        mode = mode || 'Byte';
        let newData = null;
        switch (mode) {
            case 'Numeric':
                newData = new QrNumber(data);
                break;
            case 'Alphanumeric':
                newData = new QrAlphaNum(data);
                break;
            case 'Byte':
                newData = new Qr8BitByte(data);
                break;
            default:
                throw 'mode:' + mode;
        }
        this._dataList.push(newData);
        this._dataCache = null;
    }

    isDark(row, col) {
        if (row < 0 || this._moduleCount <= row || col < 0 || this._moduleCount <= col) {
            throw row + ',' + col;
        }
        return this._modules[row][col];
    }

    getModuleCount() {
        return this._moduleCount;
    }

    make() {
        if (this._typeNumber < 1) {
            let typeNumber = 1;

            for (; typeNumber < 40; typeNumber++) {
                const rsBlocks = QRRSBlock.getRSBlocks(typeNumber, this._errorCorrectionLevel);
                const buffer = new QrBitBuffer();

                for (let i = 0; i < this._dataList.length; i++) {
                    const data = this._dataList[i];
                    buffer.put(data.getMode(), 4);
                    buffer.put(data.getLength(), QRUtil.getLengthInBits(data.getMode(), typeNumber));
                    data.write(buffer);
                }

                let totalDataCount = 0;
                for (let i = 0; i < rsBlocks.length; i++) {
                    totalDataCount += rsBlocks[i].dataCount;
                }

                if (buffer.getLengthInBits() <= totalDataCount * 8) {
                    break;
                }
            }

            this._typeNumber = typeNumber;
        }

        this._makeImpl(false, this._getBestMaskPattern());
    };

    //---------------------------------------------------------------------
    // createStringToBytes
    //---------------------------------------------------------------------

    /**
     * @param unicodeData base64 string of byte array.
     * [16bit Unicode],[16bit Bytes], ...
     * @param numChars
     */
    _createStringToBytes(unicodeData, numChars) {

        // create conversion map.

        const unicodeMap = function () {

            const bin = new Base64DecodeInputStream(unicodeData);
            const read = function () {
                const b = bin.read();
                if (b == -1) throw 'eof';
                return b;
            };

            let count = 0;
            const unicodeMap = {};
            while (true) {
                const b0 = bin.read();
                if (b0 == -1) break;
                const b1 = read();
                const b2 = read();
                const b3 = read();
                const k = String.fromCharCode((b0 << 8) | b1);
                const v = (b2 << 8) | b3;
                unicodeMap[k] = v;
                count += 1;
            }
            if (count != numChars) {
                throw count + ' != ' + numChars;
            }

            return unicodeMap;
        }();

        const unknownChar = '?'.charCodeAt(0);

        return function (s) {
            const bytes = [];
            for (let i = 0; i < s.length; i += 1) {
                const c = s.charCodeAt(i);
                if (c < 128) {
                    bytes.push(c);
                } else {
                    const b = unicodeMap[s.charAt(i)];
                    if (typeof b == 'number') {
                        if ((b & 0xff) == b) {
                            // 1byte
                            bytes.push(b);
                        } else {
                            // 2bytes
                            bytes.push(b >>> 8);
                            bytes.push(b & 0xff);
                        }
                    } else {
                        bytes.push(unknownChar);
                    }
                }
            }
            return bytes;
        };
    }

    createTableTag(cellSize = 5, margin = 4) {

        const moduleCount = this.getModuleCount();
        const marginSize = cellSize * margin;

        let qrHtml = '';

        qrHtml += '<table style="';
        qrHtml += ' border-width: 0px; border-style: none;';
        qrHtml += ' border-collapse: collapse;';
        qrHtml += ' padding: 0px; margin: ' + marginSize + 'px;';
        qrHtml += '">';
        qrHtml += '<tbody>';

        for (let r = 0; r < moduleCount; r += 1) {
            qrHtml += '<tr>';
            for (let c = 0; c < moduleCount; c += 1) {
                qrHtml += '<td style="';
                qrHtml += ' border-width: 0px; border-style: none;';
                qrHtml += ' border-collapse: collapse;';
                qrHtml += ' padding: 0px; margin: 0px;';
                qrHtml += ' width: ' + cellSize + 'px;';
                qrHtml += ' height: ' + cellSize + 'px;';
                qrHtml += ' background-color: ';
                qrHtml += this.isDark(r, c) ? '#000000' : '#ffffff';
                qrHtml += ';';
                qrHtml += '"/>';
            }

            qrHtml += '</tr>';
        }

        qrHtml += '</tbody>';
        qrHtml += '</table>';

        return qrHtml;
    }

    createSvgTag(cellSize = 5, margin = 4) {

        const moduleCount = this.getModuleCount();
        const size = (moduleCount + margin * 2) * cellSize;

        let qrSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}"`;
        qrSvg += ` viewBox="0 0 ${size} ${size}"`;
        qrSvg += ' preserveAspectRatio="xMinYMin meet" >';
        qrSvg += `<defs><g id="qrblock"><rect x="0" y="0" width="${cellSize}" height="${cellSize}" fill="black"></g></defs>`;
        qrSvg += '<rect width="100%" height="100%" fill="white" cx="0" cy="0"/>';

        for (let r = 0; r < moduleCount; r += 1) {
            for (let c = 0; c < moduleCount; c += 1) {
                if (this.isDark(r, c)) {
                    const mr = (r + margin) * cellSize;
                    const mc = (c + margin) * cellSize;
                    qrSvg += `<use x="${mc}" y="${mr}" xlink:href="#qrblock" />`;
                }
            }
        }

        qrSvg += '</svg>';
        return qrSvg;
    }

    createGifDataURL(width, height, getPixel) {
        const gif = new GifImage(width, height);
        for (let y = 0; y < height; y += 1) {
            for (let x = 0; x < width; x += 1) {
                gif.setPixel(x, y, getPixel(x, y));
            }
        }

        const b = new ByteArrayOutputStream();
        gif.write(b);

        const base64 = new Base64EncodeOutputStream();
        const bytes = b.toByteArray();
        for (let i = 0; i < bytes.length; i += 1) {
            base64.writeByte(bytes[i]);
        }
        base64.flush();

        return 'data:image/gif;base64,' + base64;
    }

    createDataURL(cellSize = 5, margin = 4) {
        const size = (this.getModuleCount() + margin * 2) * cellSize;
        const min = margin * cellSize;
        const max = size - margin * cellSize;

        const that = this;
        return this.createGifDataURL(size, size, function (x, y) {
            if (min <= x && x < max && min <= y && y < max) {
                const c = Math.floor((x - min) / cellSize);
                const r = Math.floor((y - min) / cellSize);
                return that.isDark(r, c) ? 0 : 1;
            } else {
                return 1;
            }
        });
    }

    createImgTag(cellSize = 5, margin = 4) {
        const size = (this.getModuleCount() + margin * 2) * cellSize;

        let img = '<img';
        img += `\u0020src="${this.createDataURL(cellSize, margin)}"`;
        img += `\u0020width="${size}"\u0020height="${size}"`;
        img += '/>';
        return img;
    }

    renderTo2dContext(cellSize = 5, margin = 4) {
        const moduleCount = this.getModuleCount();
        const size = (moduleCount + margin * 2) * cellSize;

        const canvas = document.createElement('canvas');
        canvas.width = size;
        canvas.height = size;

        const ctx = canvas.getContext("2d");

        ctx.fillStyle = 'white';
        ctx.fillRect(0, 0, size, size);

        ctx.fillStyle = 'black';
        for (let r = 0; r < moduleCount; r += 1) {
            for (let c = 0; c < moduleCount; c += 1) {
                if (this.isDark(r, c)) {
                    const mr = (r + margin) * cellSize;
                    const mc = (c + margin) * cellSize;
                    ctx.fillRect(mc, mr, cellSize, cellSize);
                }
            }
        }

        return canvas;

    }


    _makeImpl(test, maskPattern) {
        this._moduleCount = this._typeNumber * 4 + 17;
        this._modules = function (moduleCount) {
            const modules = new Array(moduleCount);
            for (let row = 0; row < moduleCount; row += 1) {
                modules[row] = new Array(moduleCount);
                for (let col = 0; col < moduleCount; col += 1) {
                    modules[row][col] = null;
                }
            }
            return modules;
        }(this._moduleCount);

        this._setupPositionProbePattern(0, 0);
        this._setupPositionProbePattern(this._moduleCount - 7, 0);
        this._setupPositionProbePattern(0, this._moduleCount - 7);
        this._setupPositionAdjustPattern();
        this._setupTimingPattern();
        this._setupTypeInfo(test, maskPattern);

        if (this._typeNumber >= 7) {
            this._setupTypeNumber(test);
        }

        if (this._dataCache == null) {
            this._dataCache = this._createData(this._typeNumber, this._errorCorrectionLevel, this._dataList);
        }

        this._mapData(this._dataCache, maskPattern);
    }

    _setupPositionProbePattern(row, col) {
        for (let r = -1; r <= 7; r += 1) {
            if (row + r <= -1 || this._moduleCount <= row + r) continue;

            for (let c = -1; c <= 7; c += 1) {
                if (col + c <= -1 || this._moduleCount <= col + c) continue;
                if ((0 <= r && r <= 6 && (c == 0 || c == 6))
                    || (0 <= c && c <= 6 && (r == 0 || r == 6))
                    || (2 <= r && r <= 4 && 2 <= c && c <= 4)) {
                    this._modules[row + r][col + c] = true;
                } else {
                    this._modules[row + r][col + c] = false;
                }
            }
        }
    }

    _getBestMaskPattern() {
        let minLostPoint = 0;
        let pattern = 0;

        for (let i = 0; i < 8; i += 1) {
            this._makeImpl(true, i);
            let lostPoint = QRUtil.getLostPoint(this);
            if (i == 0 || minLostPoint > lostPoint) {
                minLostPoint = lostPoint;
                pattern = i;
            }
        }

        return pattern;
    }

    _setupTimingPattern() {
        for (let r = 8; r < this._moduleCount - 8; r += 1) {
            if (this._modules[r][6] != null) {
                continue;
            }
            this._modules[r][6] = (r % 2 == 0);
        }

        for (let c = 8; c < this._moduleCount - 8; c += 1) {
            if (this._modules[6][c] != null) {
                continue;
            }
            this._modules[6][c] = (c % 2 == 0);
        }
    }

    _setupPositionAdjustPattern() {
        const pos = QRUtil.getPatternPosition(this._typeNumber);

        for (let i = 0; i < pos.length; i += 1) {

            for (let j = 0; j < pos.length; j += 1) {

                const row = pos[i];
                const col = pos[j];

                if (this._modules[row][col] != null) {
                    continue;
                }

                for (let r = -2; r <= 2; r += 1) {

                    for (let c = -2; c <= 2; c += 1) {

                        if (r == -2 || r == 2 || c == -2 || c == 2 || (r == 0 && c == 0)) {
                            this._modules[row + r][col + c] = true;
                        } else {
                            this._modules[row + r][col + c] = false;
                        }
                    }
                }
            }
        }
    }

    _setupTypeNumber(test) {

        const bits = QRUtil.getBCHTypeNumber(this._typeNumber);

        for (let i = 0; i < 18; i += 1) {
            const mod = (!test && ((bits >> i) & 1) == 1);
            this._modules[Math.floor(i / 3)][i % 3 + this._moduleCount - 8 - 3] = mod;
        }

        for (let i = 0; i < 18; i += 1) {
            const mod = (!test && ((bits >> i) & 1) == 1);
            this._modules[i % 3 + this._moduleCount - 8 - 3][Math.floor(i / 3)] = mod;
        }
    }

    _setupTypeInfo(test, maskPattern) {

        const data = (this._errorCorrectionLevel << 3) | maskPattern;
        const bits = QRUtil.getBCHTypeInfo(data);

        // vertical
        for (let i = 0; i < 15; i += 1) {

            const mod = (!test && ((bits >> i) & 1) == 1);

            if (i < 6) {
                this._modules[i][8] = mod;
            } else if (i < 8) {
                this._modules[i + 1][8] = mod;
            } else {
                this._modules[this._moduleCount - 15 + i][8] = mod;
            }
        }

        // horizontal
        for (let i = 0; i < 15; i += 1) {

            const mod = (!test && ((bits >> i) & 1) == 1);

            if (i < 8) {
                this._modules[8][this._moduleCount - i - 1] = mod;
            } else if (i < 9) {
                this._modules[8][15 - i - 1 + 1] = mod;
            } else {
                this._modules[8][15 - i - 1] = mod;
            }
        }

        // fixed module
        this._modules[this._moduleCount - 8][8] = (!test);
    }

    _mapData(data, maskPattern) {

        let inc = -1;
        let row = this._moduleCount - 1;
        let bitIndex = 7;
        let byteIndex = 0;
        const maskFunc = QRUtil.getMaskFunction(maskPattern);

        for (let col = this._moduleCount - 1; col > 0; col -= 2) {

            if (col == 6) col -= 1;

            while (true) {

                for (let c = 0; c < 2; c += 1) {

                    if (this._modules[row][col - c] == null) {

                        let dark = false;

                        if (byteIndex < data.length) {
                            dark = (((data[byteIndex] >>> bitIndex) & 1) == 1);
                        }

                        const mask = maskFunc(row, col - c);

                        if (mask) {
                            dark = !dark;
                        }

                        this._modules[row][col - c] = dark;
                        bitIndex -= 1;

                        if (bitIndex == -1) {
                            byteIndex += 1;
                            bitIndex = 7;
                        }
                    }
                }

                row += inc;

                if (row < 0 || this._moduleCount <= row) {
                    row -= inc;
                    inc = -inc;
                    break;
                }
            }
        }
    }

    _createBytes(buffer, rsBlocks) {

        let offset = 0;

        let maxDcCount = 0;
        let maxEcCount = 0;

        const dcdata = new Array(rsBlocks.length);
        const ecdata = new Array(rsBlocks.length);

        for (let r = 0; r < rsBlocks.length; r += 1) {

            const dcCount = rsBlocks[r].dataCount;
            const ecCount = rsBlocks[r].totalCount - dcCount;

            maxDcCount = Math.max(maxDcCount, dcCount);
            maxEcCount = Math.max(maxEcCount, ecCount);

            dcdata[r] = new Array(dcCount);

            for (let i = 0; i < dcdata[r].length; i += 1) {
                dcdata[r][i] = 0xff & buffer.getBuffer()[i + offset];
            }
            offset += dcCount;

            const rsPoly = QRUtil.getErrorCorrectPolynomial(ecCount);
            const rawPoly = new QrPolynomial(dcdata[r], rsPoly.getLength() - 1);

            const modPoly = rawPoly.mod(rsPoly);
            ecdata[r] = new Array(rsPoly.getLength() - 1);
            for (let i = 0; i < ecdata[r].length; i += 1) {
                const modIndex = i + modPoly.getLength() - ecdata[r].length;
                ecdata[r][i] = (modIndex >= 0) ? modPoly.getAt(modIndex) : 0;
            }
        }

        let totalCodeCount = 0;
        for (let i = 0; i < rsBlocks.length; i += 1) {
            totalCodeCount += rsBlocks[i].totalCount;
        }

        const data = new Array(totalCodeCount);
        let index = 0;

        for (let i = 0; i < maxDcCount; i += 1) {
            for (let r = 0; r < rsBlocks.length; r += 1) {
                if (i < dcdata[r].length) {
                    data[index] = dcdata[r][i];
                    index += 1;
                }
            }
        }

        for (let i = 0; i < maxEcCount; i += 1) {
            for (let r = 0; r < rsBlocks.length; r += 1) {
                if (i < ecdata[r].length) {
                    data[index] = ecdata[r][i];
                    index += 1;
                }
            }
        }

        return data;
    }

    _createData(typeNumber, errorCorrectionLevel, dataList) {

        const rsBlocks = QRRSBlock.getRSBlocks(typeNumber, errorCorrectionLevel);

        const buffer = new QrBitBuffer();

        for (let i = 0; i < dataList.length; i += 1) {
            const data = dataList[i];
            buffer.put(data.getMode(), 4);
            buffer.put(data.getLength(), QRUtil.getLengthInBits(data.getMode(), typeNumber));
            data.write(buffer);
        }

        // calc num max data.
        let totalDataCount = 0;
        for (let i = 0; i < rsBlocks.length; i += 1) {
            totalDataCount += rsBlocks[i].dataCount;
        }

        if (buffer.getLengthInBits() > totalDataCount * 8) {
            throw 'code length overflow. (' + buffer.getLengthInBits() + '>' + totalDataCount * 8 + ')';
        }

        // end code
        if (buffer.getLengthInBits() + 4 <= totalDataCount * 8) {
            buffer.put(0, 4);
        }

        // padding
        while (buffer.getLengthInBits() % 8 != 0) {
            buffer.putBit(false);
        }

        // padding
        const PAD0 = 0xEC;
        const PAD1 = 0x11;

        while (true) {

            if (buffer.getLengthInBits() >= totalDataCount * 8) {
                break;
            }
            buffer.put(PAD0, 8);

            if (buffer.getLengthInBits() >= totalDataCount * 8) {
                break;
            }
            buffer.put(PAD1, 8);
        }

        return this._createBytes(buffer, rsBlocks);
    }

    _escapeXml(s) {
        let escaped = '';
        for (let i = 0; i < s.length; i += 1) {
            switch (s.charAt(i)) {
                case '<': escaped += '&lt;'; break;
                case '>': escaped += '&gt;'; break;
                case '&': escaped += '&amp;'; break;
                case '"': escaped += '&quot;'; break;
                default: escaped += c; break;
            }
        }
        return escaped;
    }



}





//---------------------------------------------------------------------
// QRMode
//---------------------------------------------------------------------

const QRMode = {
    MODE_NUMBER: 1 << 0,
    MODE_ALPHA_NUM: 1 << 1,
    MODE_8BIT_BYTE: 1 << 2,
    MODE_KANJI: 1 << 3
};

//---------------------------------------------------------------------
// QRErrorCorrectionLevel
//---------------------------------------------------------------------

const QRErrorCorrectionLevel = {
    L: 1,
    M: 0,
    Q: 3,
    H: 2
};

//---------------------------------------------------------------------
// QRMaskPattern
//---------------------------------------------------------------------

const QRMaskPattern = {
    PATTERN000: 0,
    PATTERN001: 1,
    PATTERN010: 2,
    PATTERN011: 3,
    PATTERN100: 4,
    PATTERN101: 5,
    PATTERN110: 6,
    PATTERN111: 7
};

//---------------------------------------------------------------------
// QRUtil
//---------------------------------------------------------------------

const PATTERN_POSITION_TABLE = [
    [],
    [6, 18],
    [6, 22],
    [6, 26],
    [6, 30],
    [6, 34],
    [6, 22, 38],
    [6, 24, 42],
    [6, 26, 46],
    [6, 28, 50],
    [6, 30, 54],
    [6, 32, 58],
    [6, 34, 62],
    [6, 26, 46, 66],
    [6, 26, 48, 70],
    [6, 26, 50, 74],
    [6, 30, 54, 78],
    [6, 30, 56, 82],
    [6, 30, 58, 86],
    [6, 34, 62, 90],
    [6, 28, 50, 72, 94],
    [6, 26, 50, 74, 98],
    [6, 30, 54, 78, 102],
    [6, 28, 54, 80, 106],
    [6, 32, 58, 84, 110],
    [6, 30, 58, 86, 114],
    [6, 34, 62, 90, 118],
    [6, 26, 50, 74, 98, 122],
    [6, 30, 54, 78, 102, 126],
    [6, 26, 52, 78, 104, 130],
    [6, 30, 56, 82, 108, 134],
    [6, 34, 60, 86, 112, 138],
    [6, 30, 58, 86, 114, 142],
    [6, 34, 62, 90, 118, 146],
    [6, 30, 54, 78, 102, 126, 150],
    [6, 24, 50, 76, 102, 128, 154],
    [6, 28, 54, 80, 106, 132, 158],
    [6, 32, 58, 84, 110, 136, 162],
    [6, 26, 54, 82, 110, 138, 166],
    [6, 30, 58, 86, 114, 142, 170]
];
const G15 = (1 << 10) | (1 << 8) | (1 << 5) | (1 << 4) | (1 << 2) | (1 << 1) | (1 << 0);
const G18 = (1 << 12) | (1 << 11) | (1 << 10) | (1 << 9) | (1 << 8) | (1 << 5) | (1 << 2) | (1 << 0);
const G15_MASK = (1 << 14) | (1 << 12) | (1 << 10) | (1 << 4) | (1 << 1);



class QRUtil {

    static getBCHDigit(data) {
        let digit = 0;
        while (data != 0) {
            digit += 1;
            data >>>= 1;
        }
        return digit;
    }

    static getBCHTypeInfo(data) {
        let d = data << 10;
        while (this.getBCHDigit(d) - this.getBCHDigit(G15) >= 0) {
            d ^= (G15 << (this.getBCHDigit(d) - this.getBCHDigit(G15)));
        }
        return ((data << 10) | d) ^ G15_MASK;
    };

    static getBCHTypeNumber(data) {
        let d = data << 12;
        while (this.getBCHDigit(d) - this.getBCHDigit(G18) >= 0) {
            d ^= (G18 << (this.getBCHDigit(d) - this.getBCHDigit(G18)));
        }
        return (data << 12) | d;
    };

    static getPatternPosition(typeNumber) {
        return PATTERN_POSITION_TABLE[typeNumber - 1];
    };

    static getMaskFunction(maskPattern) {

        switch (maskPattern) {

            case QRMaskPattern.PATTERN000:
                return function (i, j) { return (i + j) % 2 == 0; };
            case QRMaskPattern.PATTERN001:
                return function (i, j) { return i % 2 == 0; };
            case QRMaskPattern.PATTERN010:
                return function (i, j) { return j % 3 == 0; };
            case QRMaskPattern.PATTERN011:
                return function (i, j) { return (i + j) % 3 == 0; };
            case QRMaskPattern.PATTERN100:
                return function (i, j) { return (Math.floor(i / 2) + Math.floor(j / 3)) % 2 == 0; };
            case QRMaskPattern.PATTERN101:
                return function (i, j) { return (i * j) % 2 + (i * j) % 3 == 0; };
            case QRMaskPattern.PATTERN110:
                return function (i, j) { return ((i * j) % 2 + (i * j) % 3) % 2 == 0; };
            case QRMaskPattern.PATTERN111:
                return function (i, j) { return ((i * j) % 3 + (i + j) % 2) % 2 == 0; };

            default:
                throw 'bad maskPattern:' + maskPattern;
        }
    };

    static getErrorCorrectPolynomial(errorCorrectLength) {
        let a = new QrPolynomial([1], 0);
        for (let i = 0; i < errorCorrectLength; i += 1) {
            a = a.multiply(new QrPolynomial([1, QRMath.gexp(i)], 0));
        }
        return a;
    };

    static getLengthInBits(mode, type) {

        if (1 <= type && type < 10) {

            // 1 - 9

            switch (mode) {
                case QRMode.MODE_NUMBER: return 10;
                case QRMode.MODE_ALPHA_NUM: return 9;
                case QRMode.MODE_8BIT_BYTE: return 8;
                case QRMode.MODE_KANJI: return 8;
                default:
                    throw 'mode:' + mode;
            }

        } else if (type < 27) {

            // 10 - 26

            switch (mode) {
                case QRMode.MODE_NUMBER: return 12;
                case QRMode.MODE_ALPHA_NUM: return 11;
                case QRMode.MODE_8BIT_BYTE: return 16;
                case QRMode.MODE_KANJI: return 10;
                default:
                    throw 'mode:' + mode;
            }

        } else if (type < 41) {

            // 27 - 40

            switch (mode) {
                case QRMode.MODE_NUMBER: return 14;
                case QRMode.MODE_ALPHA_NUM: return 13;
                case QRMode.MODE_8BIT_BYTE: return 16;
                case QRMode.MODE_KANJI: return 12;
                default:
                    throw 'mode:' + mode;
            }

        } else {
            throw 'type:' + type;
        }
    };

    static getLostPoint(qrcode) {
        const moduleCount = qrcode.getModuleCount();
        let lostPoint = 0;

        // LEVEL1
        for (let row = 0; row < moduleCount; row += 1) {
            for (let col = 0; col < moduleCount; col += 1) {
                let sameCount = 0;
                const dark = qrcode.isDark(row, col);

                for (let r = -1; r <= 1; r += 1) {
                    if (row + r < 0 || moduleCount <= row + r) {
                        continue;
                    }

                    for (let c = -1; c <= 1; c += 1) {
                        if (col + c < 0 || moduleCount <= col + c) {
                            continue;
                        }

                        if (r == 0 && c == 0) {
                            continue;
                        }

                        if (dark == qrcode.isDark(row + r, col + c)) {
                            sameCount += 1;
                        }
                    }
                }

                if (sameCount > 5) {
                    lostPoint += (3 + sameCount - 5);
                }
            }
        };

        // LEVEL2
        for (let row = 0; row < moduleCount - 1; row += 1) {
            for (let col = 0; col < moduleCount - 1; col += 1) {
                let count = 0;
                if (qrcode.isDark(row, col)) count += 1;
                if (qrcode.isDark(row + 1, col)) count += 1;
                if (qrcode.isDark(row, col + 1)) count += 1;
                if (qrcode.isDark(row + 1, col + 1)) count += 1;
                if (count == 0 || count == 4) {
                    lostPoint += 3;
                }
            }
        }

        // LEVEL3

        for (let row = 0; row < moduleCount; row += 1) {
            for (let col = 0; col < moduleCount - 6; col += 1) {
                if (qrcode.isDark(row, col)
                    && !qrcode.isDark(row, col + 1)
                    && qrcode.isDark(row, col + 2)
                    && qrcode.isDark(row, col + 3)
                    && qrcode.isDark(row, col + 4)
                    && !qrcode.isDark(row, col + 5)
                    && qrcode.isDark(row, col + 6)) {
                    lostPoint += 40;
                }
            }
        }

        for (let col = 0; col < moduleCount; col += 1) {
            for (let row = 0; row < moduleCount - 6; row += 1) {
                if (qrcode.isDark(row, col)
                    && !qrcode.isDark(row + 1, col)
                    && qrcode.isDark(row + 2, col)
                    && qrcode.isDark(row + 3, col)
                    && qrcode.isDark(row + 4, col)
                    && !qrcode.isDark(row + 5, col)
                    && qrcode.isDark(row + 6, col)) {
                    lostPoint += 40;
                }
            }
        }

        // LEVEL4

        let darkCount = 0;

        for (let col = 0; col < moduleCount; col += 1) {
            for (let row = 0; row < moduleCount; row += 1) {
                if (qrcode.isDark(row, col)) {
                    darkCount += 1;
                }
            }
        }

        let ratio = Math.abs(100 * darkCount / moduleCount / moduleCount - 50) / 5;
        lostPoint += ratio * 10;

        return lostPoint;
    };


}

//---------------------------------------------------------------------
// QRMath
//---------------------------------------------------------------------

const EXP_TABLE = new Array(256);
const LOG_TABLE = new Array(256);

// initialize tables
!function () {
    for (let i = 0; i < 8; i += 1) {
        EXP_TABLE[i] = 1 << i;
    }
    for (let i = 8; i < 256; i += 1) {
        EXP_TABLE[i] = EXP_TABLE[i - 4]
            ^ EXP_TABLE[i - 5]
            ^ EXP_TABLE[i - 6]
            ^ EXP_TABLE[i - 8];
    }
    for (let i = 0; i < 255; i += 1) {
        LOG_TABLE[EXP_TABLE[i]] = i;
    }
}();


class QRMath {

    static glog(n) {

        if (n < 1) {
            throw 'glog(' + n + ')';
        }

        return LOG_TABLE[n];
    }

    static gexp(n) {

        while (n < 0) {
            n += 255;
        }

        while (n >= 256) {
            n -= 255;
        }

        return EXP_TABLE[n];
    }
}

//---------------------------------------------------------------------
// QrPolynomial
//---------------------------------------------------------------------

class QrPolynomial {

    constructor(num, shift) {
        if (typeof num.length == 'undefined') {
            throw num.length + '/' + shift;
        }

        // _num
        let offset = 0;
        while (offset < num.length && num[offset] == 0) {
            offset += 1;
        }
        this._num = new Array(num.length - offset + shift);
        for (let i = 0; i < num.length - offset; i += 1) {
            this._num[i] = num[i + offset];
        }
    }

    getAt(index) {
        return this._num[index];
    }

    getLength() {
        return this._num.length;
    }

    multiply(e) {
        const num = new Array(this.getLength() + e.getLength() - 1);

        for (let i = 0; i < this.getLength(); i += 1) {
            for (let j = 0; j < e.getLength(); j += 1) {
                num[i + j] ^= QRMath.gexp(QRMath.glog(this.getAt(i)) + QRMath.glog(e.getAt(j)));
            }
        }

        return new QrPolynomial(num, 0);
    }

    mod(e) {
        if (this.getLength() - e.getLength() < 0) {
            return this;
        }

        const ratio = QRMath.glog(this.getAt(0)) - QRMath.glog(e.getAt(0));

        const num = new Array(this.getLength());
        for (let i = 0; i < this.getLength(); i += 1) {
            num[i] = this.getAt(i);
        }

        for (let i = 0; i < e.getLength(); i += 1) {
            num[i] ^= QRMath.gexp(QRMath.glog(e.getAt(i)) + ratio);
        }

        // recursive call
        return (new QrPolynomial(num, 0)).mod(e);
    };

}

//---------------------------------------------------------------------
// QRRSBlock
//---------------------------------------------------------------------

const RS_BLOCK_TABLE = [

    // L
    // M
    // Q
    // H

    // 1
    [1, 26, 19],
    [1, 26, 16],
    [1, 26, 13],
    [1, 26, 9],

    // 2
    [1, 44, 34],
    [1, 44, 28],
    [1, 44, 22],
    [1, 44, 16],

    // 3
    [1, 70, 55],
    [1, 70, 44],
    [2, 35, 17],
    [2, 35, 13],

    // 4
    [1, 100, 80],
    [2, 50, 32],
    [2, 50, 24],
    [4, 25, 9],

    // 5
    [1, 134, 108],
    [2, 67, 43],
    [2, 33, 15, 2, 34, 16],
    [2, 33, 11, 2, 34, 12],

    // 6
    [2, 86, 68],
    [4, 43, 27],
    [4, 43, 19],
    [4, 43, 15],

    // 7
    [2, 98, 78],
    [4, 49, 31],
    [2, 32, 14, 4, 33, 15],
    [4, 39, 13, 1, 40, 14],

    // 8
    [2, 121, 97],
    [2, 60, 38, 2, 61, 39],
    [4, 40, 18, 2, 41, 19],
    [4, 40, 14, 2, 41, 15],

    // 9
    [2, 146, 116],
    [3, 58, 36, 2, 59, 37],
    [4, 36, 16, 4, 37, 17],
    [4, 36, 12, 4, 37, 13],

    // 10
    [2, 86, 68, 2, 87, 69],
    [4, 69, 43, 1, 70, 44],
    [6, 43, 19, 2, 44, 20],
    [6, 43, 15, 2, 44, 16],

    // 11
    [4, 101, 81],
    [1, 80, 50, 4, 81, 51],
    [4, 50, 22, 4, 51, 23],
    [3, 36, 12, 8, 37, 13],

    // 12
    [2, 116, 92, 2, 117, 93],
    [6, 58, 36, 2, 59, 37],
    [4, 46, 20, 6, 47, 21],
    [7, 42, 14, 4, 43, 15],

    // 13
    [4, 133, 107],
    [8, 59, 37, 1, 60, 38],
    [8, 44, 20, 4, 45, 21],
    [12, 33, 11, 4, 34, 12],

    // 14
    [3, 145, 115, 1, 146, 116],
    [4, 64, 40, 5, 65, 41],
    [11, 36, 16, 5, 37, 17],
    [11, 36, 12, 5, 37, 13],

    // 15
    [5, 109, 87, 1, 110, 88],
    [5, 65, 41, 5, 66, 42],
    [5, 54, 24, 7, 55, 25],
    [11, 36, 12, 7, 37, 13],

    // 16
    [5, 122, 98, 1, 123, 99],
    [7, 73, 45, 3, 74, 46],
    [15, 43, 19, 2, 44, 20],
    [3, 45, 15, 13, 46, 16],

    // 17
    [1, 135, 107, 5, 136, 108],
    [10, 74, 46, 1, 75, 47],
    [1, 50, 22, 15, 51, 23],
    [2, 42, 14, 17, 43, 15],

    // 18
    [5, 150, 120, 1, 151, 121],
    [9, 69, 43, 4, 70, 44],
    [17, 50, 22, 1, 51, 23],
    [2, 42, 14, 19, 43, 15],

    // 19
    [3, 141, 113, 4, 142, 114],
    [3, 70, 44, 11, 71, 45],
    [17, 47, 21, 4, 48, 22],
    [9, 39, 13, 16, 40, 14],

    // 20
    [3, 135, 107, 5, 136, 108],
    [3, 67, 41, 13, 68, 42],
    [15, 54, 24, 5, 55, 25],
    [15, 43, 15, 10, 44, 16],

    // 21
    [4, 144, 116, 4, 145, 117],
    [17, 68, 42],
    [17, 50, 22, 6, 51, 23],
    [19, 46, 16, 6, 47, 17],

    // 22
    [2, 139, 111, 7, 140, 112],
    [17, 74, 46],
    [7, 54, 24, 16, 55, 25],
    [34, 37, 13],

    // 23
    [4, 151, 121, 5, 152, 122],
    [4, 75, 47, 14, 76, 48],
    [11, 54, 24, 14, 55, 25],
    [16, 45, 15, 14, 46, 16],

    // 24
    [6, 147, 117, 4, 148, 118],
    [6, 73, 45, 14, 74, 46],
    [11, 54, 24, 16, 55, 25],
    [30, 46, 16, 2, 47, 17],

    // 25
    [8, 132, 106, 4, 133, 107],
    [8, 75, 47, 13, 76, 48],
    [7, 54, 24, 22, 55, 25],
    [22, 45, 15, 13, 46, 16],

    // 26
    [10, 142, 114, 2, 143, 115],
    [19, 74, 46, 4, 75, 47],
    [28, 50, 22, 6, 51, 23],
    [33, 46, 16, 4, 47, 17],

    // 27
    [8, 152, 122, 4, 153, 123],
    [22, 73, 45, 3, 74, 46],
    [8, 53, 23, 26, 54, 24],
    [12, 45, 15, 28, 46, 16],

    // 28
    [3, 147, 117, 10, 148, 118],
    [3, 73, 45, 23, 74, 46],
    [4, 54, 24, 31, 55, 25],
    [11, 45, 15, 31, 46, 16],

    // 29
    [7, 146, 116, 7, 147, 117],
    [21, 73, 45, 7, 74, 46],
    [1, 53, 23, 37, 54, 24],
    [19, 45, 15, 26, 46, 16],

    // 30
    [5, 145, 115, 10, 146, 116],
    [19, 75, 47, 10, 76, 48],
    [15, 54, 24, 25, 55, 25],
    [23, 45, 15, 25, 46, 16],

    // 31
    [13, 145, 115, 3, 146, 116],
    [2, 74, 46, 29, 75, 47],
    [42, 54, 24, 1, 55, 25],
    [23, 45, 15, 28, 46, 16],

    // 32
    [17, 145, 115],
    [10, 74, 46, 23, 75, 47],
    [10, 54, 24, 35, 55, 25],
    [19, 45, 15, 35, 46, 16],

    // 33
    [17, 145, 115, 1, 146, 116],
    [14, 74, 46, 21, 75, 47],
    [29, 54, 24, 19, 55, 25],
    [11, 45, 15, 46, 46, 16],

    // 34
    [13, 145, 115, 6, 146, 116],
    [14, 74, 46, 23, 75, 47],
    [44, 54, 24, 7, 55, 25],
    [59, 46, 16, 1, 47, 17],

    // 35
    [12, 151, 121, 7, 152, 122],
    [12, 75, 47, 26, 76, 48],
    [39, 54, 24, 14, 55, 25],
    [22, 45, 15, 41, 46, 16],

    // 36
    [6, 151, 121, 14, 152, 122],
    [6, 75, 47, 34, 76, 48],
    [46, 54, 24, 10, 55, 25],
    [2, 45, 15, 64, 46, 16],

    // 37
    [17, 152, 122, 4, 153, 123],
    [29, 74, 46, 14, 75, 47],
    [49, 54, 24, 10, 55, 25],
    [24, 45, 15, 46, 46, 16],

    // 38
    [4, 152, 122, 18, 153, 123],
    [13, 74, 46, 32, 75, 47],
    [48, 54, 24, 14, 55, 25],
    [42, 45, 15, 32, 46, 16],

    // 39
    [20, 147, 117, 4, 148, 118],
    [40, 75, 47, 7, 76, 48],
    [43, 54, 24, 22, 55, 25],
    [10, 45, 15, 67, 46, 16],

    // 40
    [19, 148, 118, 6, 149, 119],
    [18, 75, 47, 31, 76, 48],
    [34, 54, 24, 34, 55, 25],
    [20, 45, 15, 61, 46, 16]
];

class QRRSBlock {

    static getRSBlocks(typeNumber, errorCorrectionLevel) {

        let rsBlock;
        switch (errorCorrectionLevel) {
            case QRErrorCorrectionLevel.L:
                rsBlock = RS_BLOCK_TABLE[(typeNumber - 1) * 4 + 0];
                break;
            case QRErrorCorrectionLevel.M:
                rsBlock = RS_BLOCK_TABLE[(typeNumber - 1) * 4 + 1];
                break;
            case QRErrorCorrectionLevel.Q:
                rsBlock = RS_BLOCK_TABLE[(typeNumber - 1) * 4 + 2];
                break;
            case QRErrorCorrectionLevel.H:
                rsBlock = RS_BLOCK_TABLE[(typeNumber - 1) * 4 + 3];
                break;
            default:
                rsBlock = undefined;
        }

        if (typeof rsBlock == 'undefined') {
            throw 'bad rs block @ typeNumber:' + typeNumber + '/errorCorrectionLevel:' + errorCorrectionLevel;
        }

        const length = rsBlock.length / 3;
        const list = [];

        for (let i = 0; i < length; i += 1) {
            const count = rsBlock[i * 3 + 0];
            const totalCount = rsBlock[i * 3 + 1];
            const dataCount = rsBlock[i * 3 + 2];

            for (let j = 0; j < count; j += 1) {
                list.push({ totalCount, dataCount });
            }
        }

        return list;
    }

}

//---------------------------------------------------------------------
// QrBitBuffer
//---------------------------------------------------------------------

class QrBitBuffer {
    constructor() {
        this._buffer = [];
        this._length = 0;
    }

    getBuffer() {
        return this._buffer;
    }

    getAt(index) {
        const bufIndex = Math.floor(index / 8);
        return ((this._buffer[bufIndex] >>> (7 - index % 8)) & 1) == 1;
    }

    put(num, length) {
        for (let i = 0; i < length; i += 1) {
            this.putBit(((num >>> (length - i - 1)) & 1) == 1);
        }
    }

    getLengthInBits() {
        return this._length;
    };

    putBit(bit) {
        const bufIndex = Math.floor(this._length / 8);
        if (this._buffer.length <= bufIndex) {
            this._buffer.push(0);
        }

        if (bit) {
            this._buffer[bufIndex] |= (0x80 >>> (this._length % 8));
        }

        this._length += 1;
    }

}

//---------------------------------------------------------------------
// QrNumber
//---------------------------------------------------------------------

class QrNumber {
    constructor(data) {
        this._mode = QRMode.MODE_NUMBER;
        this._data = data;
    }

    getMode() {
        return this._mode;
    };

    getLength() {
        return this._data.length;
    };

    write(buffer) {
        let data = this._data;
        let i = 0;
        while (i + 2 < data.length) {
            buffer.put(this._strToNum(data.substring(i, i + 3)), 10);
            i += 3;
        }

        if (i < data.length) {
            if (data.length - i == 1) {
                buffer.put(this._strToNum(data.substring(i, i + 1)), 4);
            } else if (data.length - i == 2) {
                buffer.put(this._strToNum(data.substring(i, i + 2)), 7);
            }
        }
    };

    _strToNum(s) {
        let num = 0;
        for (let i = 0; i < s.length; i += 1) {
            num = num * 10 + this._chatToNum(s.charAt(i));
        }
        return num;
    }

    _chatToNum(c) {
        if ('0' <= c && c <= '9') {
            return c.charCodeAt(0) - '0'.charCodeAt(0);
        }
        throw 'illegal char :' + c;
    };


}

//---------------------------------------------------------------------
// QrAlphaNum 混合字符模式 字符集 0-9 A-Z 及特殊字符 
//---------------------------------------------------------------------

class QrAlphaNum {
    constructor(data) {
        this._mode = QRMode.MODE_ALPHA_NUM;
        this._data = data;
    }

    getMode() {
        return this._mode;
    }

    getLength() {
        return this._data.length;
    }

    write(buffer) {
        let s = this._data;
        let i = 0;

        while (i + 1 < s.length) {
            buffer.put(
                this._getCode(s.charAt(i)) * 45 +
                this._getCode(s.charAt(i + 1)), 11);
            i += 2;
        }

        if (i < s.length) {
            buffer.put(this._getCode(s.charAt(i)), 6);
        }
    }

    _getCode(c) {
        if ('0' <= c && c <= '9') {
            return c.charCodeAt(0) - '0'.charCodeAt(0);
        } else if ('A' <= c && c <= 'Z') {
            return c.charCodeAt(0) - 'A'.charCodeAt(0) + 10;
        } else {
            switch (c) {
                case ' ': return 36;
                case '$': return 37;
                case '%': return 38;
                case '*': return 39;
                case '+': return 40;
                case '-': return 41;
                case '.': return 42;
                case '/': return 43;
                case ':': return 44;
                default:
                    throw 'illegal char :' + c;
            }
        }
    };

}

//---------------------------------------------------------------------
// Qr8BitByte
//---------------------------------------------------------------------

class Qr8BitByte {
    constructor(data) {
        this._mode = QRMode.MODE_8BIT_BYTE;
        this._bytes = this._stringToBytes(data);
    }

    // support utf8
    _stringToBytes(str) {
        let utf8 = [];
        for (let i = 0; i < str.length; i++) {
            let charcode = str.charCodeAt(i);
            if (charcode < 0x80) utf8.push(charcode);
            else if (charcode < 0x800) {
                utf8.push(0xc0 | (charcode >> 6), 0x80 | (charcode & 0x3f));
            }
            else if (charcode < 0xd800 || charcode >= 0xe000) {
                utf8.push(0xe0 | (charcode >> 12), 0x80 | ((charcode >> 6) & 0x3f), 0x80 | (charcode & 0x3f));
            }
            else {
                i++;
                // UTF-16 encodes 0x10000-0x10FFFF by subtracting 0x10000 and splitting the 20 bits of 0x0-0xFFFFF into two halves
                charcode = 0x10000 + (((charcode & 0x3ff) << 10) | (str.charCodeAt(i) & 0x3ff));
                utf8.push(0xf0 | (charcode >> 18), 0x80 | ((charcode >> 12) & 0x3f), 0x80 | ((charcode >> 6) & 0x3f), 0x80 | (charcode & 0x3f));
            }
        }
        return utf8;
    }

    getMode() {
        return this._mode;
    }

    getLength() {
        return this._bytes.length;
    }

    write(buffer) {
        for (let i = 0; i < this._bytes.length; i += 1) {
            buffer.put(this._bytes[i], 8);
        }
    }
}


//=====================================================================
// GIF Support etc.
//

//---------------------------------------------------------------------
// classByteArrayOutputStream
//---------------------------------------------------------------------

class ByteArrayOutputStream {
    constructor() {
        this._bytes = [];
    }

    writeByte(b) {
        this._bytes.push(b & 0xff);
    };

    writeShort(i) {
        this.writeByte(i);
        this.writeByte(i >>> 8);
    };

    writeBytes(b, off, len) {
        off = off || 0;
        len = len || b.length;
        for (let i = 0; i < len; i += 1) {
            this.writeByte(b[i + off]);
        }
    };

    writeString(s) {
        for (let i = 0; i < s.length; i += 1) {
            this.writeByte(s.charCodeAt(i));
        }
    };

    toByteArray() {
        return this._bytes;
    };

    toString() {
        let s = '';
        s += '[';
        for (let i = 0; i < this._bytes.length; i += 1) {
            if (i > 0) {
                s += ',';
            }
            s += this._bytes[i];
        }
        s += ']';
        return s;
    };

}


class BitOutputStream {
    constructor(out) {
        this._out = out;
        this._bitLength = 0;
        this._bitBuffer = 0;
    }

    write(data, length) {

        if ((data >>> length) != 0) {
            throw 'length over';
        }

        while (this._bitLength + length >= 8) {
            this._out.writeByte(0xff & ((data << this._bitLength) | this._bitBuffer));
            length -= (8 - this._bitLength);
            data >>>= (8 - this._bitLength);
            this._bitBuffer = 0;
            this._bitLength = 0;
        }

        this._bitBuffer = (data << this._bitLength) | this._bitBuffer;
        this._bitLength = this._bitLength + length;
    }

    flush() {
        if (this._bitLength > 0) {
            this._out.writeByte(this._bitBuffer);
        }
    }

}


//---------------------------------------------------------------------
// Base64EncodeOutputStream
//---------------------------------------------------------------------

class Base64EncodeOutputStream {
    constructor() {
        this._buffer = 0;
        this._buflen = 0;
        this._length = 0;
        this._base64 = '';
    }

    writeEncoded(b) {
        this._base64 += String.fromCharCode(this.encode(b & 0x3f));
    }

    encode(n) {
        if (n < 0) {
            // error.
        } else if (n < 26) {
            return 0x41 + n;
        } else if (n < 52) {
            return 0x61 + (n - 26);
        } else if (n < 62) {
            return 0x30 + (n - 52);
        } else if (n == 62) {
            return 0x2b;
        } else if (n == 63) {
            return 0x2f;
        }
        throw 'n:' + n;
    }

    writeByte(n) {
        this._buffer = (this._buffer << 8) | (n & 0xff);
        this._buflen += 8;
        this._length += 1;

        while (this._buflen >= 6) {
            this.writeEncoded(this._buffer >>> (this._buflen - 6));
            this._buflen -= 6;
        }
    }

    flush() {
        if (this._buflen > 0) {
            this.writeEncoded(this._buffer << (6 - this._buflen));
            this._buffer = 0;
            this._buflen = 0;
        }

        if (this._length % 3 != 0) {
            // padding
            const padlen = 3 - this._length % 3;
            for (let i = 0; i < padlen; i += 1) {
                this._base64 += '=';
            }
        }
    }

    toString() {
        return this._base64;
    }

}

//---------------------------------------------------------------------
// Base64DecodeInputStream
//---------------------------------------------------------------------

class Base64DecodeInputStream {
    constructor(str) {
        this._str = str;
        this._pos = 0;
        this._buffer = 0;
        this._buflen = 0;
    }

    read() {
        while (this._buflen < 8) {
            if (this._pos >= this._str.length) {
                if (this._buflen == 0) {
                    return -1;
                }
                throw 'unexpected end of file./' + _buflen;
            }

            let c = this._str.charAt(this._pos);
            this._pos += 1;

            if (c == '=') {
                this._buflen = 0;
                return -1;
            } else if (c.match(/^\s$/)) {
                // ignore if whitespace.
                continue;
            }

            this._buffer = (this._buffer << 6) | this._decode(c.charCodeAt(0));
            this._buflen += 6;
        }

        const n = (this._buffer >>> (this._buflen - 8)) & 0xff;
        this._buflen -= 8;
        return n;
    }

    _decode(c) {
        if (0x41 <= c && c <= 0x5a) {
            return c - 0x41;
        } else if (0x61 <= c && c <= 0x7a) {
            return c - 0x61 + 26;
        } else if (0x30 <= c && c <= 0x39) {
            return c - 0x30 + 52;
        } else if (c == 0x2b) {
            return 62;
        } else if (c == 0x2f) {
            return 63;
        } else {
            throw 'c:' + c;
        }
    };


}

//---------------------------------------------------------------------
// GifImage (B/W)
//---------------------------------------------------------------------

class LzwTable {
    constructor() {
        this._map = {};
        this._size = 0;
    }

    add(key) {
        if (this.contains(key)) {
            throw 'dup key:' + key;
        }
        this._map[key] = this._size;
        this._size += 1;
    };

    size() {
        return this._size;
    };

    indexOf(key) {
        return this._map[key];
    };

    contains(key) {
        return typeof this._map[key] != 'undefined';
    };

}

class GifImage {
    constructor(width, height) {
        this._width = width;
        this._height = height;
        this._data = new Array(width * height);
    }


    setPixel(x, y, pixel) {
        this._data[y * this._width + x] = pixel;
    };

    write(out) {

        //---------------------------------
        // GIF Signature
        out.writeString('GIF87a');

        //---------------------------------
        // Screen Descriptor

        out.writeShort(this._width);
        out.writeShort(this._height);

        out.writeByte(0x80); // 2bit
        out.writeByte(0);
        out.writeByte(0);

        //---------------------------------
        // Global Color Map

        // black
        out.writeByte(0x00);
        out.writeByte(0x00);
        out.writeByte(0x00);

        // white
        out.writeByte(0xff);
        out.writeByte(0xff);
        out.writeByte(0xff);

        //---------------------------------
        // Image Descriptor

        out.writeString(',');
        out.writeShort(0);
        out.writeShort(0);
        out.writeShort(this._width);
        out.writeShort(this._height);
        out.writeByte(0);

        //---------------------------------
        // Local Color Map

        //---------------------------------
        // Raster Data

        const lzwMinCodeSize = 2;
        const raster = this._getLZWRaster(lzwMinCodeSize);

        out.writeByte(lzwMinCodeSize);

        let offset = 0;

        while (raster.length - offset > 255) {
            out.writeByte(255);
            out.writeBytes(raster, offset, 255);
            offset += 255;
        }

        out.writeByte(raster.length - offset);
        out.writeBytes(raster, offset, raster.length - offset);
        out.writeByte(0x00);

        //---------------------------------
        // GIF Terminator
        out.writeString(';');
    }



    _getLZWRaster(lzwMinCodeSize) {
        const clearCode = 1 << lzwMinCodeSize;
        const endCode = (1 << lzwMinCodeSize) + 1;
        let bitLength = lzwMinCodeSize + 1;

        // Setup LZWTable
        const table = new LzwTable();

        for (let i = 0; i < clearCode; i += 1) {
            table.add(String.fromCharCode(i));
        }
        table.add(String.fromCharCode(clearCode));
        table.add(String.fromCharCode(endCode));

        const byteOut = new ByteArrayOutputStream();
        const bitOut = new BitOutputStream(byteOut);

        // clear code
        bitOut.write(clearCode, bitLength);

        let dataIndex = 0;

        let s = String.fromCharCode(this._data[dataIndex]);
        dataIndex += 1;

        while (dataIndex < this._data.length) {

            let c = String.fromCharCode(this._data[dataIndex]);
            dataIndex += 1;

            if (table.contains(s + c)) {

                s = s + c;

            } else {

                bitOut.write(table.indexOf(s), bitLength);

                if (table.size() < 0xfff) {

                    if (table.size() == (1 << bitLength)) {
                        bitLength += 1;
                    }

                    table.add(s + c);
                }

                s = c;
            }
        }

        bitOut.write(table.indexOf(s), bitLength);

        // end code
        bitOut.write(endCode, bitLength);

        bitOut.flush();

        return byteOut.toByteArray();
    };

}

window.QrCode = QrCode;
