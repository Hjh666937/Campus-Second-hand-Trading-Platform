const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

// 演示账号。学生与管理员共用同一个登录入口，失败提示不做区分。
const MOCK_USERS = [
  {
    id: 1,
    account: '20261116',
    password: '20261116',
    nickname: '林小满',
    campus: '东校区',
    gender: 'female',
    role: 'student',
    credit: 98
  },
  {
    id: 2,
    account: 'admin',
    password: 'admin123',
    nickname: '平台管理员',
    campus: '校务中心',
    gender: 'secret',
    role: 'admin',
    credit: 100
  }
]

// 注册的账号存本地，保证「注册完能直接登录」
const STORAGE_KEY = 'mock-registered-users'
const RESERVED_ACCOUNTS = ['admin', 'administrator', 'root']

function readRegistered() {
  try {
    const list = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
    return Array.isArray(list) ? list : []
  } catch (error) {
    return []
  }
}

function saveRegistered(list) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(list))
}

function fail(message, code) {
  const error = new Error(message)
  error.code = code
  return error
}

// 初始密码规则：账号后 6 位，不足 6 位用 123456
export const INITIAL_PASSWORD_RULE = '账号后 6 位数字（不足 6 位为 123456）'

function buildInitialPassword(account) {
  const tail = String(account).slice(-6)
  return tail.length === 6 ? tail : '123456'
}

/**
 * 管理员重置用户密码
 * 只重置为初始密码，不返回明文，管理员看不到用户的新密码。
 */
export async function mockResetPassword(account) {
  await delay(320)

  if (account === 'admin') {
    throw fail('管理员账号不能在这里重置', 403)
  }

  const registered = readRegistered()
  const registeredUser = registered.find((user) => user.account === account)
  if (registeredUser) {
    registeredUser.password = buildInitialPassword(account)
    saveRegistered(registered)
    return true
  }

  const builtinUser = MOCK_USERS.find((user) => user.account === account)
  if (!builtinUser) {
    throw fail('用户不存在', 404)
  }

  builtinUser.password = buildInitialPassword(account)
  return true
}

/**
 * 登录 Mock
 * 结构与后端 POST /api/auth/login 的返回保持一致，接入后端时无需改动页面代码。
 */
export async function mockLogin({ account, password }) {
  await delay(600)

  const allUsers = [...MOCK_USERS, ...readRegistered()]
  const matched = allUsers.find(
    (user) => user.account === account && user.password === password
  )

  // 账号不存在或密码错误统一抛出同一句提示，不暴露账号是否注册
  if (!matched) {
    throw fail('账号或密码错误', 401)
  }

  const { password: _password, ...profile } = matched

  return {
    token: `mock-token-${profile.role}-${Date.now()}`,
    user: profile
  }
}

/**
 * 注册 Mock
 * 只能注册学生账号，管理员账号不允许通过任何入口自助注册。
 */
export async function mockRegister({ account, nickname, campus, gender, password }) {
  await delay(700)

  const normalized = account.trim().toLowerCase()

  if (RESERVED_ACCOUNTS.includes(normalized)) {
    throw fail('该账号为管理员保留账号，不能注册', 403)
  }

  const exists = [...MOCK_USERS, ...readRegistered()].some(
    (user) => user.account.toLowerCase() === normalized
  )

  if (exists) {
    throw fail('该学号已注册，请直接登录', 409)
  }

  const user = {
    id: Date.now(),
    account: account.trim(),
    password,
    nickname,
    campus,
    gender,
    role: 'student',
    credit: 100
  }

  saveRegistered([...readRegistered(), user])

  const { password: _password, ...profile } = user
  return profile
}

/**
 * 修改密码 Mock
 * 先校验当前密码，再更新；注册用户写回 localStorage，内置账号改内存。
 */
export async function mockChangePassword({ account, oldPassword, newPassword }) {
  await delay(400)

  const registered = readRegistered()
  const registeredUser = registered.find((user) => user.account === account)

  if (registeredUser) {
    if (registeredUser.password !== oldPassword) {
      throw fail('当前密码不正确', 400)
    }
    registeredUser.password = newPassword
    saveRegistered(registered)
    return true
  }

  const builtinUser = MOCK_USERS.find((user) => user.account === account)
  if (!builtinUser) {
    throw fail('用户不存在', 404)
  }

  if (builtinUser.password !== oldPassword) {
    throw fail('当前密码不正确', 400)
  }
  builtinUser.password = newPassword
  return true
}
