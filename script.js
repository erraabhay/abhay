// Load CryptoJS for encryption
function generateRandomKey(length) {
    const charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let key = '';
    for (let i = 0; i < length; i++) {
      const randomIndex = Math.floor(Math.random() * charset.length);
      key += charset[randomIndex];
    }
    return key;
  }
  
  // Utility function to encrypt a message
  function encryptMessage(message, password) {
    return CryptoJS.AES.encrypt(message, password).toString();
  }
  
  // Utility function to decrypt a message
  function decryptMessage(encryptedMessage, password) {
    const bytes = CryptoJS.AES.decrypt(encryptedMessage, password);
    return bytes.toString(CryptoJS.enc.Utf8);
  }
  
  // Event listeners to prevent default form submission
  $('button.encode, button.decode').click(function(event) {
    event.preventDefault();
  });
  
  // Preview functions remain the same as provided earlier...
  
  function encodeMessage() {
    $(".error").hide();
    $(".binary").hide();
  
    const text = $("textarea.message").val();
    const userPassword = prompt("Set a password for encrypting your message:");
    
    if (!userPassword) {
      alert('Password is required for encryption.');
      return;
    }
  
    // Generate a random E2EE key
    const e2eeKey = generateRandomKey(16);
    alert(`Your encryption key (E2EE Key) is: ${e2eeKey}. Please copy and save it.`);
  
    // Encrypt the message using the E2EE key and user password
    const encryptedMessage = encryptMessage(text, userPassword + e2eeKey);
  
    // Binary conversion logic remains unchanged...
    var binaryMessage = "";
    for (let i = 0; i < encryptedMessage.length; i++) {
      var binaryChar = encryptedMessage[i].charCodeAt(0).toString(2);
      while (binaryChar.length < 8) {
        binaryChar = "0" + binaryChar;
      }
      binaryMessage += binaryChar;
    }
    $('.binary textarea').text(binaryMessage);
  
    // Image manipulation logic remains unchanged...
    const $originalCanvas = $('.original canvas');
    const $nulledCanvas = $('.nulled canvas');
    const $messageCanvas = $('.message canvas');
    const originalContext = $originalCanvas[0].getContext("2d");
    const nulledContext = $nulledCanvas[0].getContext("2d");
    const messageContext = $messageCanvas[0].getContext("2d");
    const width = $originalCanvas[0].width;
    const height = $originalCanvas[0].height;
  
    if ((binaryMessage.length * 8) > (width * height * 3)) {
      $(".error").text("Text too long for chosen image....").fadeIn();
      return;
    }
  
    $nulledCanvas.prop({ 'width': width, 'height': height });
    $messageCanvas.prop({ 'width': width, 'height': height });
  
    var original = originalContext.getImageData(0, 0, width, height);
    var pixel = original.data;
    for (var i = 0, n = pixel.length; i < n; i += 4) {
      for (var offset = 0; offset < 3; offset++) {
        if (pixel[i + offset] % 2 != 0) {
          pixel[i + offset]--;
        }
      }
    }
    nulledContext.putImageData(original, 0, 0);
  
    var message = nulledContext.getImageData(0, 0, width, height);
    pixel = message.data;
    let counter = 0;
    for (var i = 0, n = pixel.length; i < n; i += 4) {
      for (var offset = 0; offset < 3; offset++) {
        if (counter < binaryMessage.length) {
          pixel[i + offset] += parseInt(binaryMessage[counter]);
          counter++;
        } else {
          break;
        }
      }
    }
    messageContext.putImageData(message, 0, 0);
  
    $(".binary").fadeIn();
    $(".images .nulled").fadeIn();
    $(".images .message").fadeIn();
  };
  
  function decodeMessage() {
    const e2eeKey = prompt("Enter the E2EE key:");
    const userPassword = prompt("Enter the password:");
  
    if (!e2eeKey || !userPassword) {
      alert('Both E2EE key and password are required for decryption.');
      return;
    }
  
    const $originalCanvas = $('.decode canvas');
    const originalContext = $originalCanvas[0].getContext("2d");
    const original = originalContext.getImageData(0, 0, $originalCanvas.width(), $originalCanvas.height());
    let binaryMessage = "";
    const pixel = original.data;
    for (var i = 0, n = pixel.length; i < n; i += 4) {
      for (var offset = 0; offset < 3; offset++) {
        binaryMessage += (pixel[i + offset] % 2).toString();
      }
    }
  
    let encryptedMessage = "";
    for (let i = 0; i < binaryMessage.length; i += 8) {
      let byte = binaryMessage.slice(i, i + 8);
      encryptedMessage += String.fromCharCode(parseInt(byte, 2));
    }
  
    try {
      const decryptedMessage = decryptMessage(encryptedMessage, userPassword + e2eeKey);
      if (decryptedMessage) {
        $('.binary-decode textarea').text(decryptedMessage);
        $('.binary-decode').fadeIn();
        alert('Message decoded successfully!');
      } else {
        alert('Invalid E2EE key or password.');
      }
    } catch (e) {
      alert('Decryption failed. Invalid E2EE key or password.');
    }
  };
  